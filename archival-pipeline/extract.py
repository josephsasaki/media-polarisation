'''This is an extract script for the archive pipeline. it connects the rds database and converts the data into a pandas dataframe'''
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


def get_connection() -> connection:
    '''Gets a connection to the RDS database'''
    load_dotenv()
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_HOST = os.getenv("DB_HOST")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT = os.getenv("DB_PORT")
    return (psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} host={DB_HOST} password={DB_PASSWORD} port={DB_PORT}"))


def fetch_joined_dataframe(conn: connection) -> pd.DataFrame:
    '''fetches data from the RDS database and reads it into a dataframe'''
    three_months_ago = datetime.now() - timedelta(days=90)

    query = """
        SELECT
            a.article_id, at.article_topic_id, a.article_headline, a.article_url, a.article_published_date,
            a.article_subjectivity, a.article_polarity, no.news_outlet_name, t.topic_name, at.positive,
            at.negative, at.neutral, at.compound
        FROM article_topic at
        JOIN article a ON a.article_id = at.article_id
        JOIN topic t ON t.topic_id = at.topic_id
        JOIN news_outlet no ON no.news_outlet_id = a.news_outlet_id
        WHERE a.article_published_date <%s
    """
    return pd.read_sql(query, conn, params=three_months_ago)


if __name__ == "__main__":
    conn = get_connection()
    fetch_joined_dataframe(conn)
