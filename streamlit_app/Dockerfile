FROM python:3.10
LABEL description="This is a streamlit app container"
EXPOSE 8501
WORKDIR /streamlit_app
COPY requirements.txt ./requirements.txt 
COPY src ./src
RUN pip3 install -r requirements.txt
COPY . .
CMD streamlit run src/App.py \
    --server.headless true \
    --browser.serverAddress="0.0.0.0" \
    --server.enableCORS false \
    --browser.gatherUsageStats false