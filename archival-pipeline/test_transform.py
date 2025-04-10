'''
    Test script for the transform part of the pipeline.
'''

import os
from unittest.mock import patch
import pandas as pd
import pytest
from transform import DataFrameToCSVTransformer


def test_default_output_path_is_absolute():
    '''Test that the default output path resolves to an absolute path.'''
    transformer = DataFrameToCSVTransformer()
    output_path = transformer._DataFrameToCSVTransformer__output_path  # pylint: disable=protected-access
    assert os.path.isabs(output_path)
    assert output_path.endswith("tmp/data.csv")


def test_custom_output_path_is_absolute():
    '''Test that a custom output path is correctly resolved to absolute.'''
    transformer = DataFrameToCSVTransformer("relative/path/to/file.csv")
    output_path = transformer._DataFrameToCSVTransformer__output_path  # pylint: disable=protected-access
    assert os.path.isabs(output_path)
    assert output_path.endswith("relative/path/to/file.csv")


@patch("pandas.DataFrame.to_csv")
def test_to_csv_called_with_correct_arguments(mock_to_csv):
    '''Test that the DataFrame's to_csv is called with the correct arguments.'''
    df = pd.DataFrame({"x": [1, 2]})
    transformer = DataFrameToCSVTransformer("tmp/output.csv")
    transformer.save_dataframe_to_csv(df)

    expected_path = transformer._DataFrameToCSVTransformer__output_path  # pylint: disable=protected-access
    mock_to_csv.assert_called_once_with(expected_path, index=False)


def test_file_is_actually_written(tmp_path):
    '''Test that the file is actually created with correct content.'''
    df = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    file_path = tmp_path / "output.csv"
    transformer = DataFrameToCSVTransformer(str(file_path))
    transformer.save_dataframe_to_csv(df)

    assert file_path.exists()

    # Read it back and verify contents
    written_df = pd.read_csv(file_path)
    pd.testing.assert_frame_equal(df, written_df)


def test_empty_dataframe_still_writes_file(tmp_path):
    '''Test that even an empty DataFrame creates a CSV file (with headers).'''
    df = pd.DataFrame(columns=["x", "y"])
    file_path = tmp_path / "empty.csv"
    transformer = DataFrameToCSVTransformer(str(file_path))
    transformer.save_dataframe_to_csv(df)

    assert file_path.exists()
    with open(file_path, encoding='utf-8') as f:
        header = f.readline().strip()
        assert header == "x,y"


@patch("pandas.DataFrame.to_csv")
def test_to_csv_raises_exception_if_fails(mock_to_csv):
    '''Test that if to_csv raises an exception, it bubbles up.'''
    df = pd.DataFrame({"x": [1, 2]})
    transformer = DataFrameToCSVTransformer("tmp/will_fail.csv")
    mock_to_csv.side_effect = IOError("Disk full!")

    with pytest.raises(IOError, match="Disk full!"):
        transformer.save_dataframe_to_csv(df)
