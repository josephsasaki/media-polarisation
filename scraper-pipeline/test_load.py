import pytest
from unittest.mock import MagicMock, patch, call
from models import Article, TopicAnalysis
from datetime import datetime
from load import DatabaseManager


@pytest.fixture
def mock_connection():
    with patch("load.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
@patch.dict("os.environ", {
    "DB_NAME": "test_db",
    "DB_USERNAME": "user",
    "DB_PASSWORD": "pass",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
})
def db_manager(mock_connection):
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    # Mock query return values
    mock_cursor.fetchall.side_effect = [
        [("Guardian", 1), ("Express", 2)],  # news outlet map
        [("Politics", 10), ("Economy", 20)]  # topic map
    ]
    return DatabaseManager()


def test_get_valid_topics(db_manager):
    assert sorted(db_manager.get_valid_topics()) == ["Economy", "Politics"]


def test_insert_articles_assigns_ids(db_manager, mock_connection):
    mock_cursor = mock_connection.cursor.return_value.__enter__.return_value

    article = Article(
        news_outlet="Guardian",
        headline="Test Headline",
        url="http://test.com",
        published_date=datetime.now(),
        body="Test body"
    )
    article.set_subjectivity(0.5)
    article.set_polarity(0.3)
    article.set_sentiments(0.1, 0.7, 0.2, 0.4)

    mock_cursor.fetchone.return_value = [123]

    db_manager._insert_articles([article])
    assert article.get_insert_values({"Guardian": 1})[0] == 1
    assert article._Article__article_id == 123


def test_insert_into_database_combines_inserts(db_manager, mock_connection):
    mock_cursor = mock_connection.cursor.return_value.__enter__.return_value

    topic = TopicAnalysis("Economy", ["inflation"])
    topic.set_sentiments(0.1, 0.2, 0.3, 0.4)

    article = Article("Express", "Test", "http://url", datetime.now(), "Body")
    article.set_subjectivity(0.4)
    article.set_polarity(0.2)
    article.set_sentiments(0.1, 0.2, 0.3, 0.4)
    article.set_topics_analyses([topic])

    mock_cursor.fetchone.return_value = [42]

    db_manager.insert_into_database([article])
    assert article._Article__article_id == 42
