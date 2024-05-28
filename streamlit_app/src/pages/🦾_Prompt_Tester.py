import streamlit as st
from few_shot import build_prompt
import boto3

st.set_page_config(
    page_title="Prompt Tester",
    page_icon="🦾",
)
st.title("Prompt Tester 🦾")
st.markdown(
    """
    Aqui vas a poder observar los prompt templates que se utilizan dependiendo el ticket 
    seleccionado
    """
)
def main():
    bedrock = boto3.client(region_name= 'us-east-1', service_name='bedrock-runtime')
    with st.form('my_form'):
        text = st.text_area(label='Enter text:', value=' ')
        st.write('You entered:', text)
        submitted = st.form_submit_button('Submit')
        
        if submitted:
            promptTemplate = build_prompt(text, bedrock)
            prompt = promptTemplate.generate_prompt()
            st.write(prompt.format(doc_text=text))

if __name__ == '__main__': 
    main()