from tqdm.auto import tqdm
import boto3
import json
from botocore.config import Config
import pickle

from langchain_aws import ChatBedrock
from langchain.chains import LLMChain

from langchain_core.prompts import PromptTemplate
from Prompts import prompt_keypoints

config = Config(read_timeout=900) # timeout for botocore de 5 min. Por defecto es 1 min.

bedrock = boto3.client(region_name= 'us-east-1', service_name='bedrock-runtime', config=config)

def prompt_builder():
    
    prompt_key = PromptTemplate(template=prompt_keypoints, input_variables=["doc_text"])

    return prompt_key


def main (event, context):
    print('event: ',event)
    # get document
    document = event['document']
    # get document
    s3_reso = boto3.resource('s3')
    bucket_name = 'llm-showcase'
    paper_key_pkl ='document_loaders_assets/paper.pkl'
    paper_key_pdf = f'papers/{document}'
    file_pkl_path = '/tmp/paper.pkl'
    file_pdf_path = '/tmp/paper.pdf'
    s3_reso.Object(bucket_name,paper_key_pkl).download_file(file_pkl_path)
    s3_reso.Object(bucket_name,paper_key_pdf).download_file(file_pdf_path)
    # get loader from pkl
    with open(file_pkl_path, "rb") as infile:
        loader = pickle.load(infile)
    # load content
    document = loader.load()
    # summarize text
    bedrock_llm = ChatBedrock(client=bedrock, model_id="anthropic.claude-3-sonnet-20240229-v1:0")
    # Build prompt
    prompt_key = prompt_builder()
    # inference keypoints
    llm_chain2 = LLMChain(prompt=prompt_key, llm=bedrock_llm)
    llm_response_key = llm_chain2.invoke(document[0].page_content)
    print('llm_response_key: {}'.format(llm_response_key))

    return {
        'statusCode': 200,
        'llm_response_key': llm_response_key
    }