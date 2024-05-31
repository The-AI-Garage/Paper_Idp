import streamlit as st
from streamlit_feedback import streamlit_feedback
import re
from tqdm.auto import tqdm
import boto3
import json
#from langchain_community.document_loaders import AmazonTextractPDFLoader
import os
import time

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

lambda_client = boto3.client(region_name= 'us-east-1', service_name='lambda')
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
        # file_s3_path = "s3://llm-showcase/papers/" + file.name 
        # loader = AmazonTextractPDFLoader(file_s3_path)
        # document = loader.load()
        # function_params = {"document": document}
        # call orquestrator lambda
        function_params = {"filename": file.name}
        msg.toast(f"Leyendo {file.name} 🧙‍♂️")
        with st.spinner('Wait for it...'):
            response = lambda_client.invoke(
                FunctionName='LangchainOrquestrator',
                Payload=json.dumps(function_params),
            )
        msg.toast("Interesante lectura 🤔...")
        time.sleep(1)
        msg.toast("Preparando resultado 🔧")
        #st.success(f"Response from lambda!")
        
        # parse response
        response_json = json.load(response['Payload'])
        #st.write('response', response)
        #st.write('response_json', response_json)
        llm_classifier_resp = response_json['llm_response_clas']
        llm_key_resp = response_json['llm_response_key']
        llm_summarization = response_json['summarization']

        classifier_output = re.findall("<label>(.*?)</label>", llm_classifier_resp['text'])
        summarization_output = llm_summarization
        extracted_author = re.findall("<author>(.*?)</author>", llm_key_resp['text'])
        extracted_title = re.findall("<title>(.*?)</title>", llm_key_resp['text'])

        st.write('Categoria: ', classifier_output[0])
        st.write('Resumen: ', summarization_output)
        st.write('Autor: ', extracted_author[0])
        st.write('Titulo: ', extracted_title[0])

if __name__ == '__main__': 
    main()