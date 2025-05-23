'''
    This file tests the S3Manager class.
'''

import os
from datetime import date
from unittest.mock import patch, MagicMock, mock_open
import pytest
from s3_manager import S3Manager


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    '''Mock required AWS environment variables.'''
    monkeypatch.setenv("ACCESS_KEY", "fake-access-key")
    monkeypatch.setenv("SECRET_ACCESS_KEY", "fake-secret")
    monkeypatch.setenv("BUCKET_REGION", "eu-west-2")
    monkeypatch.setenv("BUCKET_NAME", "my-fake-bucket")


@patch("s3_manager.boto3.client")
def test_s3_client_initialization(mock_boto_client):
    '''Ensure boto3 client is initialized with correct arguments.'''
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    s3 = S3Manager("tmp/test.csv")

    mock_boto_client.assert_called_once_with(
        "s3",
        aws_access_key_id="fake-access-key",
        aws_secret_access_key="fake-secret",
        region_name="eu-west-2"
    )
    assert s3._S3Manager__client_s3 == mock_client  # pylint: disable=protected-access


def test_bucket_key_generation():
    '''Test the S3 key generated for a given cutoff date.'''
    s3 = S3Manager("tmp/test.csv")
    cutoff = date(2025, 4, 5)
    expected_key = "2025/04/04.csv"
    # pylint: disable=protected-access
    result_key = s3._create_bucket_key(cutoff)
    assert result_key == expected_key


@patch("s3_manager.boto3.client")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake,data\n1,2")
def test_upload_csv_to_bucket(mock_file_open, mock_boto_client):
    '''Test that the CSV file is uploaded correctly to S3.'''
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    s3 = S3Manager("tmp/test.csv")
    cutoff = date(2025, 4, 5)

    s3.upload_csv_to_bucket(cutoff)

    expected_key = "2025/04/04.csv"
    mock_file_open.assert_called_once_with(
        s3._S3Manager__output_path, 'rb')  # pylint: disable=protected-access
    mock_client.put_object.assert_called_once_with(
        Bucket="my-fake-bucket",
        Key=expected_key,
        Body=mock_file_open.return_value
    )


@patch("s3_manager.boto3.client")
def test_output_path_is_absolute(_):
    '''Test that the output path is resolved to an absolute path.'''
    s3 = S3Manager("tmp/test.csv")
    assert os.path.isabs(
        s3._S3Manager__output_path)  # pylint: disable=protected-access


def test_missing_env_vars(monkeypatch):
    '''Ensure missing environment variables raise KeyError.'''
    monkeypatch.delenv("ACCESS_KEY", raising=False)
    monkeypatch.delenv("SECRET_ACCESS_KEY", raising=False)
    monkeypatch.delenv("BUCKET_REGION", raising=False)
    monkeypatch.delenv("BUCKET_NAME", raising=False)

    with pytest.raises(KeyError):
        S3Manager("tmp/test.csv")


@patch("s3_manager.boto3.client")
def test_get_bucket_name(mock_boto_client):  # pylint: disable=protected-access
    '''Test _get_bucket_name returns correct bucket name.'''
    s3 = S3Manager("tmp/test.csv")
    # pylint: disable=protected-access
    assert s3._get_bucket_name() == "my-fake-bucket"


def test_bucket_key_generation_leap_year():
    '''Ensure bucket key is generated correctly for leap year cutoff.'''
    s3 = S3Manager("tmp/test.csv")
    cutoff = date(2024, 3, 1)
    expected_key = "2024/02/29.csv"  # Leap day
    # pylint: disable=protected-access
    assert s3._create_bucket_key(cutoff) == expected_key


@patch("s3_manager.boto3.client")
def test_upload_csv_file_not_found(mock_boto_client):  # pylint: disable=protected-access
    '''Ensure FileNotFoundError is raised if output CSV does not exist.'''
    s3 = S3Manager("nonexistent.csv")
    with pytest.raises(FileNotFoundError):
        s3.upload_csv_to_bucket(date(2025, 4, 5))
