
import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv(override=True)
LAMBDA_CLIENT = boto3.client(
    "lambda",
    aws_access_key_id=os.environ['ACCESS_KEY'],
    aws_secret_access_key=os.environ['SECRET_ACCESS_KEY'],
    region_name=os.environ['LAMBDA_REGION']
)
PAYLOADS = [
    {
        "guardian": [
            "https://www.theguardian.com/politics/rss",
            "https://www.theguardian.com/us-news/us-politics/rss",
            "https://www.theguardian.com/world/rss"
        ],
        "express": []
    },
    {
        "guardian": [],
        "express": [
            "https://www.express.co.uk/posts/rss/139/politics",
            "https://www.express.co.uk/posts/rss/198/us",
            "https://www.express.co.uk/posts/rss/78/world"
        ]
    }
]


def lambda_handler(event=None, context=None):
    for payload in PAYLOADS:
        print(payload)
        LAMBDA_CLIENT.invoke(
            FunctionName=os.environ['WORKER_FUNCTION_NAME'],
            InvocationType="Event",  # async
            Payload=json.dumps(payload)
        )
