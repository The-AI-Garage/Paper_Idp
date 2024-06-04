import streamlit as st
import re
import boto3
import json
#from langchain_community.document_loaders import AmazonTextractPDFLoader
import os
import time
from botocore.config import Config
from langchain_community.document_loaders import PyPDFLoader

from langchain_aws import ChatBedrock
from langchain.chains.summarize import load_summarize_chain

config = Config(read_timeout=900) # timeout for botocore de 5 min. Por defecto es 1 min.

st.set_page_config(
    page_title="Biblioteca de papers",
    page_icon="🤖",
    )
st.title('IDP de papers cientificos 🤖')
st.markdown(
    """
    Aqui vas a poder obtener un resultado del classificador de papers. 
    """
)

lambda_client = boto3.client(region_name= 'us-east-1', service_name='lambda', config=config)
s3 = boto3.client('s3')

config = Config(read_timeout=900) # timeout for botocore de 5 min. Por defecto es 1 min.

bedrock = boto3.client(region_name= 'us-east-1', service_name='bedrock-runtime', config=config)

def main():
    
    st.sidebar.success("Select a function.")
    file = st.file_uploader('Sube un paper cientifico', type = ['pdf'])
    if file != None:
        msg = st.toast("Guardando documento 📝...")
        # Save the uploaded PDF file locally
        file_path = os.path.join("uploaded_files", file.name)
        if os.path.exists('uploaded_files'):
            pass
        else:
            os.mkdir('uploaded_files')
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        st.success(f"File {file.name} uploaded and saved successfully!")
         
        # convert pdf to text and load paper
        #function_params = {"filename": file.name}
        msg.toast(f"Leyendo {file.name} 🧙‍♂️")
        with st.spinner(f'Leyendo {file.name} 🧙‍♂️...'):
            loader = PyPDFLoader(file_path)
            document = loader.load()

        # get summary
        with st.spinner(f'Interesante lectura 🤔... Preparon un resumen'):
            bedrock_llm = ChatBedrock(client=bedrock, model_id="anthropic.claude-3-sonnet-20240229-v1:0")
            summary_chain = load_summarize_chain(llm=bedrock_llm, chain_type='map_reduce')
            summary = summary_chain.invoke(document)
                
        #st.write(summary['output_text'])
        summarization_output = summary['output_text']

        # # get category
        function_params_doc = {'summary': summary['output_text']}
        with st.spinner(f'Buscando la categoría para este artículo'):
            response_classifier = lambda_client.invoke(
                FunctionName='LangchainClassifier',
                Payload=json.dumps(function_params_doc),
             )
        response_classifier_json = json.load(response_classifier['Payload'])
        llm_classifier_resp = response_classifier_json['llm_response_clas']
        classifier_output = re.findall("<label>(.*?)</label>", llm_classifier_resp['text'])
        #st.write(classifier_output)
        # response_classifier_json = json.load(response_classifier['Payload'])
        # llm_classifier_resp = response_classifier_json['llm_response_clas']
        # classifier_output = re.findall("<label>(.*?)</label>", llm_classifier_resp['text'])

        # get keyinfo
        function_params_doc = {'document': document[0].page_content}
        with st.spinner(f'Extraigo más datos...'):
            response_keyinfo = lambda_client.invoke(
                FunctionName='LangchainKeyinfo',
                Payload=json.dumps(function_params_doc),
            )
        response_keyinfo_json = json.load(response_keyinfo['Payload'])
        llm_key_resp = response_keyinfo_json['llm_response_key']
        extracted_author = re.findall("<author>(.*?)</author>", llm_key_resp['text'])
        extracted_title = re.findall("<title>(.*?)</title>", llm_key_resp['text'])

        msg.toast("Preparando resultado 🔧")
        #st.success(f"Response from lambda!")

        st.write('**Categoria**: ', classifier_output[0])
        st.write('**Resumen**: ', summarization_output)
        st.write('**Autor**: ', extracted_author[0])
        st.write('**Titulo**: ', extracted_title[0])

if __name__ == '__main__': 
    main()