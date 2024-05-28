import streamlit as st
from streamlit_feedback import streamlit_feedback
import pandas as pd
import numpy as np
import re
from tqdm.auto import tqdm
import boto3

from langchain_community.chat_models import BedrockChat
from langchain.llms import Bedrock
from langchain.chains import LLMChain
from langchain_community.embeddings import BedrockEmbeddings
from few_shot import build_prompt

st.set_page_config(
    page_title="IT ticket classifier",
    page_icon="🤖",
    )
st.title('IT ticket classifier 🤖')
st.markdown(
    """
    Aqui vas a poder obtener un resultado del clasificador de tickets de IT 
    """
)

def generate_response(input_text, mmr_prompt, bedrock_client):
    prompt = mmr_prompt.generate_prompt()
    llm = BedrockChat(client=bedrock_client,region_name= 'us-east-1', model_id="anthropic.claude-3-sonnet-20240229-v1:0")
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    st.info(llm_chain.invoke(input_text))

def main():
    
    st.sidebar.success("Select a function.")
    bedrock = boto3.client(region_name= 'us-east-1', service_name='bedrock-runtime')
    with st.form('my_form'):
        text = st.text_area('Enter text:', ' ')
        submitted = st.form_submit_button('Submit')
    
        if submitted:
            promptTemplate = build_prompt(text, bedrock)
            generate_response(text, promptTemplate, bedrock)

if __name__ == '__main__': 
    main()