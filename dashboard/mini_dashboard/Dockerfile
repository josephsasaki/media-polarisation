FROM python:latest

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY dashboard.py .


CMD ["streamlit", "run", "dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]


