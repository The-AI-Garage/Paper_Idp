import boto3
import json
from botocore.config import Config

from langchain_aws import ChatBedrock
from langchain.chains.summarize import load_summarize_chain

config = Config(read_timeout=900) # timeout for botocore de 5 min. Por defecto es 1 min.

bedrock = boto3.client(region_name= 'us-east-1', service_name='bedrock-runtime', config=config)

def main (event, context):
    #convert pdf to text and load paper
    print('event: ',event)
    document = event['document']
    # summarize text
    bedrock_llm = ChatBedrock(client=bedrock, model_id="anthropic.claude-3-sonnet-20240229-v1:0")
    summary_chain = load_summarize_chain(llm=bedrock_llm, chain_type='map_reduce')
    summary = summary_chain.invoke(document)
    print('summary: {}'.format(summary))

    return {
        'statusCode': 200,
        'summarization': summary['output_text']
    }