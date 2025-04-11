FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY archiver.py .
COPY s3_manager.py .
COPY database_manager.py .
COPY transformer.py .
COPY lambda_handler.py .


CMD ["lambda_handler.lambda_handler"]