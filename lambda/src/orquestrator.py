import pandas as pd
import numpy as np
import re
from tqdm.auto import tqdm
import boto3

from langchain_community.document_loaders import AmazonTextractPDFLoader
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
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from Prompts import examples, prompt_classification, suffix_template, prompt_keypoints

bedrock = boto3.client(region_name= 'us-east-1', service_name='bedrock-runtime')

def main ():
    pass

if __name__ == '__main__': 
    main()