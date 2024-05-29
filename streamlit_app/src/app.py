import streamlit as st
from streamlit_feedback import streamlit_feedback
import re
from tqdm.auto import tqdm
import boto3
import json
from langchain_community.document_loaders import AmazonTextractPDFLoader

st.set_page_config(
    page_title="Clasificador de papers",
    page_icon="🤖",
    )
st.title('Clasificador de papers cientificos 🤖')
st.markdown(
    """
    Aqui vas a poder obtener un resultado del classificador de papers. 
    """
)

lambda_client = boto3.client(region_name= 'us-east-1', service_name='lambda')

def main():
    
    st.sidebar.success("Select a function.")
    file = st.file_uploader('Sube un paper cientifico', type = ['pdf'])
    if file != None:
        # convert pdf to text and load paper
        loader = AmazonTextractPDFLoader(file)
        document = loader.load()
        function_params = {"document": document}
        # call orquestrator lambda
        response = lambda_client.invoke(
            FunctionName='LangchainOrquestrator',
            Payload=json.dumps(function_params),
        )
        # parse response
        llm_classifier_resp = response['Payload']['llm_response_clas']
        llm_key_resp = response['Payload']['llm_response_key']
        llm_summarization = response['Payload']['summarization']

        classifier_output = re.findall("<label>(.*?)</label>", llm_classifier_resp['text'])
        summarization_output = llm_summarization
        extracted_author = re.findall("<author>(.*?)</author>", llm_key_resp['text'])
        extracted_title = re.findall("<title>(.*?)</title>", llm_key_resp['text'])

        st.write('Categoria: ', classifier_output)
        st.write('Resumen: ', classifier_output)
        st.write('Autor: ', classifier_output)
        st.write('Titulo: ', classifier_output)

if __name__ == '__main__': 
    main()