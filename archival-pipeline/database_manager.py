'''
    The following script defines the DatabaseManager, a class concerned with connecting 
    to the database. This class has two main functions, querying data to be archived, and
    then later removing those rows from the database once archiving was successful.
'''

import os
from datetime import date
import psycopg2
from psycopg2.extensions import connection
import pandas as pd


class DatabaseManager:
    '''Handles database connection and queries to the RDS.'''

    FETCH_ARTICLE_DATA_QUERY = """
        SELECT
            a.article_id,
            a.article_headline, 
            a.article_url,
            a.article_published_date, 
            a.article_subjectivity, 
            a.article_polarity,
            no.news_outlet_name, 
            t.topic_name, 
            at.article_topic_positive_sentiment, 
            at.article_topic_negative_sentiment, 
            at.article_topic_neutral_sentiment, 
            at.article_topic_compound_sentiment
        FROM article_topic at
        JOIN article a ON a.article_id = at.article_id
        JOIN topic t ON t.topic_id = at.topic_id
        JOIN news_outlet no ON no.news_outlet_id = a.news_outlet_id
        WHERE a.article_published_date < %s
    """
    DELETE_ARTICLES_QUERY = """
        DELETE FROM article WHERE article.article_id in %s;
    """

    def __init__(self) -> None:
        '''Initializes the DatabaseManager by connecting to the RDS database.'''
        self.__db_connection = self._create_connection()
        self.__data_to_archive = None

    def _create_connection(self) -> connection:
        '''Gets a connection to the RDS database'''
        return psycopg2.connect(
            database=os.environ['DB_NAME'],
            user=os.environ["DB_USERNAME"],
            host=os.environ["DB_HOST"],
            password=os.environ["DB_PASSWORD"],
            port=os.environ["DB_PORT"]
        )

    def fetch_data_to_archive(self, cut_off_date: date) -> pd.DataFrame:
        '''Fetches data from the RDS database and reads it into a dataframe'''
        data_to_archive = pd.read_sql(self.FETCH_ARTICLE_DATA_QUERY,
                                      self.__db_connection,
                                      params=(cut_off_date,))
        self.__data_to_archive = data_to_archive
        return data_to_archive

    def remove_archived_rows(self) -> None:
        '''Remove the rows which were previously queried from the database to be archived.'''
        if self.__data_to_archive is None:
            raise ValueError(
                "No data to archive. Ensure fetch_data_to_archive has called previously.")
        article_ids = tuple(int(n)
                            for n in self.__data_to_archive['article_id'].unique())
        with self.__db_connection.cursor() as cursor:
            cursor.execute(self.DELETE_ARTICLES_QUERY, (article_ids,))
        self.__db_connection.commit()

    def close_connection(self) -> None:
        '''Closes the database connection.'''
        if self.__db_connection:
            self.__db_connection.close()
