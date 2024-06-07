import streamlit as st
import re
import boto3
import json
#from langchain_community.document_loaders import AmazonTextractPDFLoader
import os
import time
from botocore.config import Config

config = Config(read_timeout=900) # timeout for botocore de 5 min. Por defecto es 1 min.

st.set_page_config(
    page_title="Biblioteca de papers",
    page_icon="🤖",
    )
st.title('IDP Documentos Cientificos 🤖')
st.markdown(
    """
    Este es un demo de IDP destinado para la extracción de información de documentos cientificos.


    Entre las categorias de documentos que reconoce el algoritmo estan:

    NLP, Objec detection, General ML, Recommenders y Neural Networks  
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

        # upload to s3
        object_key = f'papers/{file.name}'
        bucket_name = 'llm-showcase'
        s3.upload_file(file_path, bucket_name, object_key)
        st.success(f"File {file.name} uploaded and saved successfully!")
         
        # convert to pkl and text 
        msg.toast(f"Leyendo {file.name} 🧙‍♂️")
        function_params_doc = {'document': file.name}
        with st.spinner(f'Leyendo {file.name} 🧙‍♂️...'):
            response = lambda_client.invoke(
                FunctionName='ConvertToPkl',
                Payload=json.dumps(function_params_doc),
             )

        # get summary
        with st.spinner(f'Preparando resumen...'):
            response_summary = lambda_client.invoke(
                FunctionName='LangchainSummary',
                Payload=json.dumps(function_params_doc),
             )
        response_summary_json = json.load(response_summary['Payload'])
        #st.write(response_summary_json)
        summarization_output = response_summary_json['summarization']
        st.write('**Resumen**: ', summarization_output)

        # get category
        function_params_sum = {'summary': summarization_output}
        with st.spinner(f'Buscando la categoría para este artículo'):
            response_classifier = lambda_client.invoke(
                FunctionName='LangchainClassifier',
                Payload=json.dumps(function_params_sum),
             )
        response_classifier_json = json.load(response_classifier['Payload'])
        llm_classifier_resp = response_classifier_json['llm_response_clas']
        classifier_output = re.findall("<label>(.*?)</label>", llm_classifier_resp['text'])
        st.write('**Categoria**: ', classifier_output[0])

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

        st.write('**Autor**: ', extracted_author[0])
        st.write('**Titulo**: ', extracted_title[0])

        # send results to dynamo
        function_param_store = {
            'item':{
                'summary': summarization_output,
                'class': classifier_output[0],
                'author': extracted_author[0],
                'title': extracted_title[0]
            }
        }
        lambda_client.invoke(
            FunctionName='StoreInfo',
            Payload=json.dumps(function_param_store),
            )
        st.success(f"Data stored in DynamoDB!")

if __name__ == '__main__': 
    main()