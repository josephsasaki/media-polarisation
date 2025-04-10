'''
    Transform class that takes in a dataframe and turns it into a csv file.
'''

import os
import pandas as pd


class DataFrameToCSVTransformer:
    # pylint: disable=too-few-public-methods
    '''Handles transformation and local storage of data.'''

    def __init__(self, output_path: str = 'tmp/data.csv') -> None:
        '''Initializes the transformer class with'''
        self.__output_path = os.path.abspath(output_path)

    def save_dataframe_to_csv(self, df: pd.DataFrame) -> None:
        '''Saves a dataframe to a CSV file locally with a timestamped filename'''
        df.to_csv(self.__output_path, index=False)
