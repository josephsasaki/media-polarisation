FROM python:latest

WORKDIR /

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir static
WORKDIR /static
COPY static/bottom_bar.png .
COPY static/logo.png .
COPY static/title.png .
COPY static/top_bar.png .
WORKDIR /

COPY dashboard.py .
COPY database_manager.py .
COPY page1.py .
COPY page2.py .
COPY page3.py .
COPY page4.py .
COPY styling.py .
COPY welcome.py .


CMD ["streamlit", "run", "dashboard.py", "--server.port", "80", "--server.address", "0.0.0.0"]


