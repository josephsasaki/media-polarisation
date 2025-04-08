'''This is an extract script for the archive pipeline. it connects the rds database 
and converts the data into a pandas dataframe'''
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extensions import connection
import pandas as pd
from dotenv import load_dotenv


class DatabaseManager:
    '''Handles database connection and queries to the RDS.'''

    FETCH_ARTICLE_DATA_QUERY = """
            SELECT
                a.article_id, at.article_topic_id, a.article_headline, a.article_url,
                a.article_published_date, a.article_subjectivity, a.article_polarity,
                no.news_outlet_name, t.topic_name, at.article_topic_positive_sentiment, 
                at.article_topic_negative_sentiment,at.article_topic_neutral_sentiment, 
                at.article_topic_compound_sentiment
            FROM article_topic at
            JOIN article a ON a.article_id = at.article_id
            JOIN topic t ON t.topic_id = at.topic_id
            JOIN news_outlet no ON no.news_outlet_id = a.news_outlet_id
            WHERE a.article_published_date < %s
        """

    def __init__(self) -> None:
        '''Initializes the DatabaseManager by connecting to the RDS database.'''
        load_dotenv()
        self.db_connection = self._create_connection()

    def _create_connection(self) -> connection:
        '''Gets a connection to the RDS database'''
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_host = os.getenv("DB_HOST")
        db_password = os.getenv("DB_PASSWORD")
        db_port = os.getenv("DB_PORT")

        return psycopg2.connect(
            dbname=db_name,
            user=db_user,
            host=db_host,
            password=db_password,
            port=db_port
        )

    def fetch_joined_dataframe(self) -> pd.DataFrame:
        '''fetches data from the RDS database and reads it into a dataframe'''

        three_months_ago = datetime.now() - timedelta(days=90)

        return pd.read_sql(self.FETCH_ARTICLE_DATA_QUERY,
                           self.db_connection,
                           params=[three_months_ago])

    def close_connection(self) -> None:
        '''Closes the database connection.'''
        if self.db_connection:
            self.db_connection.close()


if __name__ == "__main__":
    db_manager = DatabaseManager()
    df = db_manager.fetch_joined_dataframe()
    db_manager.close_connection()
