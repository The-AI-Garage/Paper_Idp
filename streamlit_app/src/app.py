import streamlit as st
from streamlit_feedback import streamlit_feedback
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
st.title('Scientific paper classifier 🤖')
st.markdown(
    """
    Aqui vas a poder obtener un resultado del classificador de papers. 
    """
)

def main():
    
    st.sidebar.success("Select a function.")
    
    with st.form('my_form'):
        text = st.text_area('Enter text:', ' ')
        submitted = st.form_submit_button('Submit')
    
        if submitted:
            # call lambda
            pass

if __name__ == '__main__': 
    main()