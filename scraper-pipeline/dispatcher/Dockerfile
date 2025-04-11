FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY lambda_handler.py .

CMD ["lambda_handler.lambda_handler"]