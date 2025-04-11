'''
    This script defines the S3Manager class, which interacts with the S3 bucket on AWS.
'''

import os
from datetime import timedelta, date
import boto3


class S3Manager:
    # pylint: disable=too-few-public-methods
    '''Class that interacts with AWS S3 bucket'''

    def __init__(self, output_path: str = '/tmp/data.csv'):
        '''Initialise the S3 manager class.'''
        self.__output_path = os.path.abspath(output_path)
        self.__client_s3 = self._get_s3_client()
        self.__bucket_name = self._get_bucket_name()

    def _get_s3_client(self):
        '''Initialise an S3 client with boto3.'''
        client = boto3.client(
            "s3",
            aws_access_key_id=os.environ['ACCESS_KEY'],
            aws_secret_access_key=os.environ['SECRET_ACCESS_KEY'],
            region_name=os.environ['BUCKET_REGION'])
        return client

    def _get_bucket_name(self) -> str:
        '''Get the bucket name from environment variables.'''
        return os.environ['BUCKET_NAME']

    def _create_bucket_key(self, cut_off_date: date) -> str:
        '''Returns the key of the object (csv) to be stored on S3. The archived data
        is everything before the cut-off date, meaning the data comes from a day before the
        cut-off date.'''
        archive_date = cut_off_date-timedelta(days=1)
        return archive_date.strftime("%Y/%m/%d.csv")

    def upload_csv_to_bucket(self, cut_off_date: date):
        '''Upload the archived data, in the csv to the specified S3 bucket.'''
        bucket_key = self._create_bucket_key(cut_off_date)
        with open(self.__output_path, 'rb') as file:
            self.__client_s3.put_object(
                Bucket=self.__bucket_name, Key=bucket_key, Body=file)
