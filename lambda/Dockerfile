FROM python:3.10
LABEL description="This is a streamlit app container"
# Copy function code
COPY requirements.txt ${LAMBDA_TASK_ROOT} 
COPY src ${LAMBDA_TASK_ROOT}
# install dependencies
RUN pip3 install -r requirements.txt
# Set the CMD to your handler
CMD [ "app.orquestrator" ]