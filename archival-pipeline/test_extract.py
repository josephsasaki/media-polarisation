'''This file tests the DatabaseManger class from the extract.py file'''
from unittest.mock import patch, MagicMock
import pytest
from extract import DatabaseManager


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    '''Mock environment variables for database connection.'''
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PASSWORD", "sneaky_pass")
    monkeypatch.setenv("DB_PORT", "5432")


@patch("extract.psycopg2.connect")
def test_create_connection(mock_connect):
    '''Test that DatabaseManager creates a connection using the correct environment variables.'''
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    db = DatabaseManager()

    mock_connect.assert_called_once_with(
        dbname="test_db",
        user="test_user",
        host="localhost",
        password="sneaky_pass",
        port="5432"
    )

    assert db._DatabaseManager__db_connection == mock_conn  # pylint: disable=protected-access


@patch("extract.pd.read_sql")
@patch("extract.psycopg2.connect")
def test_fetch_joined_dataframe(mock_connect, mock_read_sql):
    '''Test that fetch_joined_dataframe executes the SQL query
    and returns the expected dataframe.'''
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_read_sql.return_value = "fake_df"

    db = DatabaseManager()
    result = db.fetch_joined_dataframe()

    mock_read_sql.assert_called_once()
    assert result == "fake_df"


@patch("extract.psycopg2.connect")
def test_close_connection(mock_connect):
    '''Test that the database connection is closed properly.'''
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    db = DatabaseManager()
    db.close_connection()

    mock_conn.close.assert_called_once()
