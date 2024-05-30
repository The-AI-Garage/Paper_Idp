from tqdm.auto import tqdm
import boto3

from langchain_aws import ChatBedrock
from langchain.llms import Bedrock
from langchain.chains import LLMChain
from langchain_community.embeddings import BedrockEmbeddings
from langchain.chains.summarize import load_summarize_chain

from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import (
    MaxMarginalRelevanceExampleSelector,
    SemanticSimilarityExampleSelector,
)
from langchain_community.document_loaders import AmazonTextractPDFLoader
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from Prompts import examples, prompt_classification, suffix_template, prompt_keypoints

bedrock = boto3.client(region_name= 'us-east-1', service_name='bedrock-runtime')

def prompt_builder():
    example_prompt = PromptTemplate(
        input_variables=["Text", "Output"],
        template="Text: {Text}\nOutput: {Output}",
    )
    example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
    # The list of examples available to select from.
    examples,
    # The embedding class used to produce embeddings which are used to measure semantic similarity.
    BedrockEmbeddings(model_id= 'amazon.titan-embed-text-v1'),
    # The VectorStore class that is used to store the embeddings and do a similarity search over.
    FAISS,
    # The number of examples to produce.
    k=1,
    )

    mmr_prompt = FewShotPromptTemplate(
    # We provide an ExampleSelector instead of examples.
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix=prompt_classification, #A prompt template string to put before the examples.
    suffix=suffix_template, #A prompt template string to put after the examples.
    input_variables=["doc_text"],
    )
    
    prompt_key = PromptTemplate(template=prompt_keypoints, input_variables=["doc_text"])

    return mmr_prompt, prompt_key


def main (event, context):
    #convert pdf to text and load paper
    file_name = event['Payload']['filename']
    file_s3_path = "s3://llm-showcase/papers/" + file_name
    loader = AmazonTextractPDFLoader(file_s3_path)
    document = loader.load()
    
    #document = event['Payload']['document']
    # summarize text
    bedrock_llm = ChatBedrock(client=bedrock, model_id="anthropic.claude-3-sonnet-20240229-v1:0")
    summary_chain = load_summarize_chain(llm=bedrock_llm, chain_type='map_reduce')
    summary = summary_chain.invoke(document)
    # Build prompt
    prompt_cls, prompt_key = prompt_builder()
    # inference classification
    llm_chain = LLMChain(prompt=prompt_cls, llm=bedrock_llm)
    llm_response_clas = llm_chain.invoke(summary['output_text'])
    # inference keypoints
    llm_chain2 = LLMChain(prompt=prompt_key, llm=bedrock_llm)
    llm_response_key = llm_chain2.invoke(document[0].page_content)

    return {
        'statusCode': 200,
        'llm_response_clas': llm_response_clas,
        'llm_response_key': llm_response_key,
        'summarization': summary['output_text']
    }, 

if __name__ == '__main__': 
    main()