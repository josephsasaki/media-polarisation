'''
Script for extracting insights from the rds and writing them up into a report
'''
import os
from datetime import date
from dotenv import load_dotenv
import psycopg2.extras
from psycopg2.extras import execute_values
from psycopg2.extensions import connection
import psycopg2

SENTIMENT_BY_TOPIC_QUERY = '''SELECT t.topic_name, ROUND(AVG(at.article_topic_positive_sentiment::numeric), 2)::float AS positive,
          ROUND(AVG(at.article_topic_negative_sentiment::numeric), 2)::float AS negative,
            ROUND(AVG(at.article_topic_neutral_sentiment::numeric), 2)::float AS neutral,
            ROUND(AVG(at.article_topic_compound_sentiment::numeric), 2)::float AS compound
                    FROM article_topic as at
                    JOIN topic AS t ON t.topic_id = at.topic_id
                    JOIN article AS a ON a.article_id = at.article_id
                    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                    WHERE no.news_outlet_name = %s AND a.article_published_date::DATE = %s
                    GROUP BY t.topic_name;'''

MOST_COVERED_TOPIC_QUERY = '''SELECT t.topic_name, COUNT(*) AS topic_frequency
                    FROM article_topic as at
                    JOIN topic AS t ON t.topic_id = at.topic_id
                    JOIN article AS a ON a.article_id = at.article_id
                    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                    WHERE no.news_outlet_name = %s AND a.article_published_date::DATE = %s
                    GROUP BY t.topic_name
                    ORDER BY topic_frequency DESC;'''


class ReportCreator:
    '''Class inserting article information and analysis into a rds postgres database '''

    def __init__(self) -> None:
        '''Initializes the DatabaseManager by connecting to the RDS database.'''
        load_dotenv()
        self.__db_connection = self._create_connection()

    def _create_connection(self) -> connection:
        '''Gets a connection to the RDS database'''
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USERNAME")
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

    def _create_cursor(self) -> psycopg2.extensions.cursor:
        '''Creates a new cursor for the connection'''
        return self.__db_connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

    def _get_guardian_topic_sentiment(self):
        '''Retrieves the average topic sentiments for each outlet'''
        cur = self._create_cursor()
        cur.execute(SENTIMENT_BY_TOPIC_QUERY, ('The Guardian', date.today()))
        sentiment_values = cur.fetchall()
        return sentiment_values

    def _get_express_topic_sentiment(self):
        '''Retrieves the average topic sentiments for each outlet'''
        cur = self._create_cursor()
        cur.execute(SENTIMENT_BY_TOPIC_QUERY, ('Daily Express', date.today()))
        sentiment_values = cur.fetchall()
        return sentiment_values

    def _get_guardian_frequent_topic(self):
        '''Retrieves the average topic sentiments for each outlet'''
        cur = self._create_cursor()
        cur.execute(MOST_COVERED_TOPIC_QUERY, ('The Guardian', date.today()))
        topic_frequency = cur.fetchall()
        return topic_frequency

    def _get_express_frequent_topic(self):
        '''Retrieves the average topic sentiments for each outlet'''
        cur = self._create_cursor()
        cur.execute(MOST_COVERED_TOPIC_QUERY, ('Daily Express', date.today()))
        topic_frequency = cur.fetchall()
        return topic_frequency


if __name__ == "__main__":
    ReportCreator()._get_express_frequent_topic()
