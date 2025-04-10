'''
    Archiver script.
'''

from datetime import date
from dotenv import load_dotenv
from database_manager import DatabaseManager
from transformer import DataFrameToCSVTransformer
from s3_manager import S3Manager


class Archiver:
    # pylint: disable=too-few-public-methods
    '''Class representing the high-level process of archiving data from the RDS into the 
    S3 bucket.'''

    def __init__(self, cut_off_date: date):
        '''Instantiate the archiver with the cut-off date. Any dates before this one 
        should be archived.'''
        self.__cut_off_date = cut_off_date
        self.__db_manager = DatabaseManager()
        self.__transformer = DataFrameToCSVTransformer()
        self.__loader = S3Manager()

    def run_pipeline(self) -> None:
        '''Run the entire data-pipeline for archiving.'''
        data_to_archive = self.__db_manager.fetch_data_to_archive(
            self.__cut_off_date)
        self.__transformer.save_dataframe_to_csv(data_to_archive)
        self.__loader.upload_csv_to_bucket(self.__cut_off_date)


if __name__ == "__main__":
    load_dotenv()
    archiver = Archiver(cut_off_date=date(2025, 1, 7))
    archiver.run_pipeline()
