FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY lambda_handler.py .
COPY scraper.py .
COPY extract.py .
COPY models.py .
COPY transform.py .
COPY analysis.py .
COPY load.py .

CMD ["lambda_handler.lambda_handler"]