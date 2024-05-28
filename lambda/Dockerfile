FROM python:3.10
LABEL description="This is a streamlit app container"
EXPOSE 8501
WORKDIR /lambda
COPY requirements.txt ./requirements.txt 
COPY src ./src
RUN pip3 install -r requirements.txt
COPY . .
CMD 