import streamlit as st
import re
import boto3
import json
#from langchain_community.document_loaders import AmazonTextractPDFLoader
import os
import time
from botocore.config import Config
from langchain_community.document_loaders import AmazonTextractPDFLoader
import base64

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

        #upload to s3. (Amazontextract need to pull the document from s3 went it has multiple pages)
        object_key = f'papers/{file.name}'
        bucket_name = 'llm-showcase'
        s3.upload_file(file_path, bucket_name, object_key)
        msg.toast("Documento guardado en S3 🗄️")
        time.sleep(1)
        st.success(f"File {file.name} uploaded and saved successfully in S3!")
         
        # convert pdf to text and load paper
        #function_params = {"filename": file.name}
        msg.toast(f"Leyendo {file.name} 🧙‍♂️")
        file_name = file.name
        file_s3_path = "s3://llm-showcase/papers/" + file_name
        with st.spinner(f'Leyendo {file.name} 🧙‍♂️...'):
            loader = AmazonTextractPDFLoader(file_s3_path, region_name= 'us-east-1')
            document = loader.load()
        docs = [doc.page_content for doc in document]
        function_params_doc = {"document": docs[:-1]}
        #st.write(document)
        #st.write(function_params_doc)

        # get summary
        with st.spinner(f'Interesante lectura 🤔... Preparon un resumen'):
                response_summary = lambda_client.invoke(
                FunctionName='LangchainSummary',
                Payload=json.dumps(function_params_doc)
            )
        response_summary_json = json.load(response_summary['Payload'])
        st.write(response_summary_json)
        summarization_output = response_summary_json['summarization']

        # get category
        with st.spinner(f'Buscando la categoría para este artículo'):
                response_classifier = lambda_client.invoke(
                FunctionName='LangchainClassifier',
                Payload=json.dumps(summarization_output),
            )
        response_classifier_json = json.load(response_classifier['Payload'])
        llm_classifier_resp = response_classifier_json['llm_response_clas']
        classifier_output = re.findall("<label>(.*?)</label>", llm_classifier_resp['text'])

        # get keyinfo
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