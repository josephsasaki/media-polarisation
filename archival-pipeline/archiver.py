'''
    The following script contains the high-level pipeline for the entire archival pipeline.
'''

from datetime import date, timedelta
from dotenv import load_dotenv
from database_manager import DatabaseManager
from transformer import DataFrameToCSVTransformer
from s3_manager import S3Manager


class Archiver:
    # pylint: disable=too-few-public-methods
    '''Class representing the high-level process of archiving data from the RDS into the 
    S3 bucket.'''

    def __init__(self, months_ago: int):
        '''Instantiate the archiver with the cut-off date. Any dates before this one 
        should be archived.'''
        self.__cut_off_date = date.today() - timedelta(days=months_ago*30)
        self.__db_manager = DatabaseManager()
        self.__transformer = DataFrameToCSVTransformer()
        self.__loader = S3Manager()

    def run_pipeline(self) -> None:
        '''Run the entire data-pipeline for archiving.'''
        print("Pipeline has begun.")
        data_to_archive = self.__db_manager.fetch_data_to_archive(
            self.__cut_off_date)
        print("Data to archive retrieved.")
        self.__transformer.save_dataframe_to_csv(data_to_archive)
        print("Data converted to CSV file.")
        self.__loader.upload_csv_to_bucket(self.__cut_off_date)
        print("CSV uploaded to S3 bucket.")
        self.__db_manager.remove_archived_rows()
        print("Archived rows removed from RDS")
        self.__db_manager.close_connection()
