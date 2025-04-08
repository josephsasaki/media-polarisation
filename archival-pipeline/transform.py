import os
import pandas as pd
from datetime import datetime


class DataTransformer:
    '''Handles transformation and local storage of data.'''

    def __init__(self, output_dir: str = "."):
        '''Initializes the transformer clas and sets up the output 
        directory defaulting to the current directory)'''
        self.output_dir = output_dir

    def save_dataframe_to_csv(self, df: pd.DataFrame, filename_prefix: str = "archived_data") -> str:
        '''Saves a dataframe to a CSV file locally with a timestamped filename'''
        datestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{filename_prefix}_{datestamp}.csv"
        file_path = os.path.join(self.output_dir, filename)

        df.to_csv(file_path, index=False)
        return file_path


if __name__ == "__main__":
    db_transformer = DataTransformer()
    df = "insert df from extract"
    file_path = db_transformer.save_dataframe_to_csv(df)
