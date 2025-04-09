''' Transform class that takes in a dataframe and turns it into a dated CSV'''
import os
from datetime import datetime
import pandas as pd


class DataFrameToCSVTransformer:
    '''Handles transformation and local storage of data.'''

    def __init__(self, output_dir: str = None) -> None:
        '''Initializes the transformer clas and sets up the output 
        directory defaulting to the current directory)'''
        if output_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.output_dir = script_dir
        else:
            self.output_dir = os.path.abspath(output_dir)

    def save_dataframe_to_csv(self, df: pd.DataFrame,
                              filename_prefix: str = "archived_data") -> str:
        '''Saves a dataframe to a CSV file locally with a timestamped filename'''
        datestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{filename_prefix}_{datestamp}.csv"
        file_path = os.path.join(self.output_dir, filename)

        df.to_csv(file_path, index=False)
        return file_path


if __name__ == "__main__":
    db_transformer = DataFrameToCSVTransformer()
    MOCK_DF = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    output_file_path = db_transformer.save_dataframe_to_csv(MOCK_DF)
