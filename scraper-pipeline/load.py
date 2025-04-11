'''
Script for loading article information and analysis into the rds postgres database.
'''
import os
import psycopg2
from psycopg2.extensions import connection
from models import Article


class DatabaseManager:
    '''Class managing queries to the AWS RDS.'''

    NEWS_OUTLETS_QUERY = 'SELECT news_outlet_name, news_outlet_id FROM news_outlet'
    TOPICS_QUERY = 'SELECT topic_name, topic_id FROM topic'
    ARTICLE_URLS_QUERY = 'SELECT article_url FROM article'
    ARTICLE_INSERT_QUERY = '''
        INSERT INTO article
            (
                news_outlet_id, 
                article_headline, 
                article_url, 
                article_published_date, 
                article_subjectivity, 
                article_polarity, 
                article_positive_sentiment, 
                article_neutral_sentiment, 
                article_negative_sentiment,
                article_compound_sentiment
            ) 
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING article_id;
    '''
    ARTICLE_TOPIC_INSERT_QUERY = '''
        INSERT INTO article_topic
            (
                article_id, 
                topic_id, 
                article_topic_positive_sentiment,
                article_topic_negative_sentiment, 
                article_topic_neutral_sentiment,
                article_topic_compound_sentiment
            ) 
        VALUES 
            (%s, %s, %s, %s, %s, %s);
    '''

    def __init__(self) -> None:
        '''Initializes the DatabaseManager by connecting to the RDS database.'''
        self.__connection = self._create_connection()
        self.__news_outlet_id_map = self._get_news_outlet_id_map()
        self.__topic_id_map = self._get_topic_id_map()

    def _create_connection(self) -> connection:
        '''Gets a connection to the RDS database'''
        return psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USERNAME"],
            host=os.environ["DB_HOST"],
            password=os.environ["DB_PASSWORD"],
            port=os.environ["DB_PORT"],
        )

    def _get_news_outlet_id_map(self) -> dict[str:int]:
        '''Retrieves a dictionary mapping news outlet names to ids.'''
        with self.__connection.cursor() as cur:
            cur.execute(self.NEWS_OUTLETS_QUERY)
            news_outlet_map = cur.fetchall()
        return dict(news_outlet_map)

    def _get_topic_id_map(self) -> dict[str:int]:
        '''Retrieves a dictionary mapping topic names to ids.'''
        with self.__connection.cursor() as cur:
            cur.execute(self.TOPICS_QUERY)
            topics_map = cur.fetchall()
        return dict(topics_map)

    def get_article_urls(self) -> list[str]:
        '''Retrieves the urls of the articles already in the database. These are
        used to determine whether an article has already been analysed.'''
        with self.__connection.cursor() as cur:
            cur.execute(self.ARTICLE_URLS_QUERY)
            existing_urls = [x[0] for x in cur.fetchall()]
        return existing_urls

    def get_valid_topics(self) -> list[str]:
        '''Extract a list of valid topics from the topic_id_map.'''
        return list(self.__topic_id_map.keys())

    def _insert_articles(self, articles: list[Article]) -> None:
        '''Insert articles into article table in the database. This method assigns
        the primary keys auto generated by the databased upon insertion to the articles.'''
        with self.__connection.cursor() as cur:
            for article in articles:
                cur.execute(
                    query=self.ARTICLE_INSERT_QUERY,
                    vars=article.get_insert_values(self.__news_outlet_id_map)
                )
                article.set_id(cur.fetchone()[0])
        self.__connection.commit()

    def _insert_article_topic(self, articles: list[Article]):
        '''Insert articles topics into article_topic table in the database.'''
        insert_values = []
        for article in articles:
            insert_values.extend(
                article.get_topic_analyses_insert_values(self.__topic_id_map))
        with self.__connection.cursor() as cur:
            cur.executemany(self.ARTICLE_TOPIC_INSERT_QUERY,
                            insert_values)
        self.__connection.commit()

    def insert_into_database(self, articles: list[Article]) -> None:
        '''Inserts articles and topic analysis data into the database.'''
        self._insert_articles(articles)
        self._insert_article_topic(articles)

    def close_connection(self) -> None:
        '''Closes the database connection.'''
        self.__connection.close()
