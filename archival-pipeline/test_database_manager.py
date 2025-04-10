'''
    This file tests the DatabaseManger class.
'''

from datetime import date
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
from database_manager import DatabaseManager


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    '''Mock environment variables for database connection.'''
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USERNAME", "test_user")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PASSWORD", "sneaky_pass")
    monkeypatch.setenv("DB_PORT", "5432")


@patch("database_manager.psycopg2.connect")
def test_create_connection(mock_connect):
    '''Test that DatabaseManager creates a connection using the correct environment variables.'''
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    db = DatabaseManager()
    mock_connect.assert_called_once_with(
        database="test_db",
        user="test_user",
        host="localhost",
        password="sneaky_pass",
        port="5432"
    )
    assert db._DatabaseManager__db_connection == mock_conn  # pylint: disable=protected-access


@patch("database_manager.pd.read_sql")
@patch("database_manager.psycopg2.connect")
def test_fetch_joined_dataframe(mock_connect, mock_read_sql):
    '''Test that fetch_joined_dataframe executes the SQL query
    and returns the expected dataframe.'''
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_read_sql.return_value = "fake_df"

    db = DatabaseManager()
    result = db.fetch_data_to_archive(cut_off_date=date(2025, 1, 1))

    mock_read_sql.assert_called_once()
    assert result == "fake_df"


@patch("database_manager.psycopg2.connect")
def test_remove_archived_rows_success(mock_connect):
    '''Test that remove_archived_rows deletes the correct article IDs.'''
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    db = DatabaseManager()

    # Simulate data returned from fetch_data_to_archive
    test_df = pd.DataFrame({
        "article_id": [101, 102, 103],
        "article_headline": ["a", "b", "c"]
    })
    # pylint: disable=invalid-name, protected-access
    db._DatabaseManager__data_to_archive = test_df

    db.remove_archived_rows()

    expected_ids = (101, 102, 103)
    mock_cursor.execute.assert_called_once_with(
        db.DELETE_ARTICLES_QUERY,
        (expected_ids,)
    )
    mock_conn.commit.assert_called_once()


@patch("database_manager.psycopg2.connect")
def test_remove_archived_rows_raises_if_no_data(mock_connect):
    '''Test that remove_archived_rows raises if fetch_data_to_archive was not called.'''
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    db = DatabaseManager()

    with pytest.raises(ValueError, match="No data to archive"):
        db.remove_archived_rows()


@patch("database_manager.psycopg2.connect")
def test_close_connection(mock_connect):
    '''Test that the database connection is closed properly.'''
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    db = DatabaseManager()
    db.close_connection()

    mock_conn.close.assert_called_once()
