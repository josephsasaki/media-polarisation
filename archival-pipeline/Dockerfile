FROM public.ecr.aws/lambda/python:3.11

WORKDIR /var/task

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY archiver.py ${LAMBDA_TASK_ROOT}

COPY s3_manager.py ${LAMBDA_TASK_ROOT}

COPY database_manager.py ${LAMBDA_TASK_ROOT}

COPY transformer.py ${LAMBDA_TASK_ROOT}

COPY event_handler.py ${LAMBDA_TASK_ROOT}


CMD ["event_handler.lambda_handler"]