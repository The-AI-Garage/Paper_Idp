FROM public.ecr.aws/lambda/python:3.12
LABEL description="This is a streamlit app container"
# Copy function code
COPY requirements.txt ${LAMBDA_TASK_ROOT} 
COPY converterpkl.py ${LAMBDA_TASK_ROOT}
# install dependencies
RUN pip3 install -r requirements.txt
# Set the CMD to your handler
CMD [ "converterpkl.main" ]