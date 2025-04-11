from archiver import Archiver
from dotenv import load_dotenv

load_dotenv(override=True)


def lambda_handler(event, context):
    '''AWS Lambda entrypoint for running the archive pipeline.'''
    months_ago = event.get("months_ago", 3)  
    archiver = Archiver(months_ago)
    archiver.run_pipeline()
    return {
        "statusCode": 200,
        "body": f"Archival pipeline ran for data older than {months_ago} months."
    }
