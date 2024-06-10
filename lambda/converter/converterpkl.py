import boto3
import json
from botocore.config import Config
import pickle
from langchain_community.document_loaders import PyPDFLoader


def main (event, context):
    # Init var
    s3_client = boto3.client('s3')
    s3_reso = boto3.resource('s3')
    region_name = 'us-east-1'
    bucket_name = 'llm-showcase'
    #convert pdf to text and load paper
    print('event: ',event)
    # get document
    document = event['document']
    print('document_name: {}'.format(document))
    # dowload from s3
    paper_key =f'papers/{document}'
    file_local_path = '/tmp/paper.pdf'
    s3_reso.Object(bucket_name,paper_key).download_file(file_local_path)
    # convert to text
    loader = PyPDFLoader(file_local_path)
    # serialize pkl
    pkl_path = "/tmp/paper.pkl"
    with open(pkl_path, "wb") as outfile:
        pickle.dump(loader, outfile)
	    
    # upload to s3
    object_key = 'document_loaders_assets/paper.pkl'
    s3_client.upload_file(pkl_path, bucket_name, object_key)

    return {
        'statusCode': 200,
    }