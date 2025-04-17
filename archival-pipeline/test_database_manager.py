'''
    This file tests the DatabaseManger class.
'''

from datetime import date
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
from database_manager import DatabaseManager
import psycopg2


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


@patch("database_manager.psycopg2.connect")
def test_create_connection_invalid_credentials(mock_connect):
    '''Test that an invalid database connection raises an exception.'''

    mock_connect.side_effect = psycopg2.OperationalError(
        "Faked database connection error")

    with pytest.raises(psycopg2.OperationalError, match="Faked database connection error"):
        db = DatabaseManager()


@patch("database_manager.psycopg2.connect")
def test_remove_archived_rows_with_duplicate_ids(mock_connect):
    '''Test that remove_archived_rows handles duplicate article IDs correctly.'''
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    db = DatabaseManager()

    # Simulate data with duplicate article IDs
    test_df = pd.DataFrame({
        "article_id": [101, 102, 102, 103],
        "article_headline": ["a", "b", "c", "d"]
    })
    db._DatabaseManager__data_to_archive = test_df

    db.remove_archived_rows()

    expected_ids = (101, 102, 103)  # Only unique IDs should be used
    mock_cursor.execute.assert_called_once_with(
        db.DELETE_ARTICLES_QUERY,
        (expected_ids,)
    )
    mock_conn.commit.assert_called_once()


@patch("database_manager.psycopg2.connect")
@patch("database_manager.pd.read_sql")
def test_fetch_data_to_archive_raises_error(mock_read_sql, mock_connect):
    '''Test that fetch_data_to_archive raises an error when the query fails.'''
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_read_sql.side_effect = pd.io.sql.DatabaseError(
        "Faked SQL query error")

    db = DatabaseManager()

    with pytest.raises(pd.io.sql.DatabaseError, match="Faked SQL query error"):
        db.fetch_data_to_archive(cut_off_date=date(2025, 1, 1))


@patch("database_manager.psycopg2.connect")
@patch("database_manager.pd.read_sql")
def test_fetch_data_to_archive_empty_dataframe(mock_read_sql, mock_connect):
    '''Test that fetch_data_to_archive returns an empty dataframe if no rows match the query.'''
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    # Simulate an empty result set
    mock_read_sql.return_value = pd.DataFrame(columns=[
        "article_id", "article_headline", "article_url", "article_published_date",
        "article_subjectivity", "article_polarity", "news_outlet_name", "topic_name",
        "article_topic_positive_sentiment", "article_topic_negative_sentiment",
        "article_topic_neutral_sentiment", "article_topic_compound_sentiment"
    ])

    db = DatabaseManager()
    result = db.fetch_data_to_archive(cut_off_date=date(2025, 1, 1))

    # Ensure that an empty dataframe is returned
    assert result.empty


@patch("database_manager.psycopg2.connect")
def test_remove_archived_rows_commits_once_for_duplicate_ids(mock_connect):
    '''Test that remove_archived_rows commits only once, even for duplicate article IDs.'''
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    db = DatabaseManager()

    # Simulate data with duplicate article IDs
    test_df = pd.DataFrame({
        "article_id": [101, 102, 102, 103, 103],
        "article_headline": ["a", "b", "c", "d", "e"]
    })
    db._DatabaseManager__data_to_archive = test_df

    db.remove_archived_rows()

    expected_ids = (101, 102, 103)  # Only unique IDs should be used
    mock_cursor.execute.assert_called_once_with(
        db.DELETE_ARTICLES_QUERY,
        (expected_ids,)
    )
    mock_conn.commit.assert_called_once()
