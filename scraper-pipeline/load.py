'''
Script for loading article information and analysis into the rds postgres database.
'''
import os
import time
from dotenv import load_dotenv
import psycopg2.extras
from psycopg2.extras import execute_values
from psycopg2.extensions import connection
import psycopg2
from models import Article
from extract import ExpressRSSFeedExtractor
from transform import ArticleFactory, TextAnalyser


class DatabaseManager:
    '''Class inserting article information and analysis into a rds postgres database '''

    def __init__(self, articles: list[Article]) -> None:
        '''Initializes the DatabaseManager by connecting to the RDS database.'''
        load_dotenv()
        self.articles = articles
        self.__db_connection = self._create_connection()
        self.outlet_ids = self._get_outlet_id()
        self.topic_ids = self._get_topic_id()

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

    def _get_outlet_id(self) -> dict[str:int]:
        '''Retrieves the the id of the news outlet'''
        cur = self._create_cursor()
        cur.execute('SELECT news_outlet_id, news_outlet_name FROM news_outlet')
        outlet_ids = cur.fetchall()
        cur.close()
        outlet_ids_dict = {row['news_outlet_name']: row['news_outlet_id']
                           for row in outlet_ids}
        return outlet_ids_dict

    def _get_topic_id(self) -> dict[str:int]:
        '''Retrieves the the id of the news outlet'''
        cur = self._create_cursor()
        cur.execute('SELECT topic_id, topic_name FROM topic')
        topic_ids = cur.fetchall()
        cur.close()
        topic_dict = {row['topic_name']: row['topic_id']
                      for row in topic_ids}
        return topic_dict

    def _get_article_url(self) -> dict[str:int]:
        '''Retrieves the urls of the articles already in the database'''
        cur = self._create_cursor()
        cur.execute('SELECT article_url FROM article')
        existing_urls = cur.fetchall()
        cur.close()
        return existing_urls

    def _get_formatted_article_values(self, article: list[str, float]) -> list[int, str, float]:
        '''returns the article values ready for insertion'''
        article_values = article.get_insert_values()
        outlet_id = self.outlet_ids[article_values[0]]
        article_values[0] = outlet_id
        return article_values

    def _insert_article(self) -> dict[str:int]:
        '''Inserts articles into article table'''
        article_insert_query = '''INSERT INTO article
          (news_outlet_id, article_headline, article_url, article_published_date,
          article_subjectivity, article_polarity, article_positive_sentiment,
            article_neutral_sentiment, article_negative_sentiment,
             article_compound_sentiment) 
          VALUES %s RETURNING article_id, article_url;'''
        cur = self._create_cursor()

        article_values = []
        for article in self.articles:
            article_values.append(tuple(self._get_formatted_article_values(
                article)))

        execute_values(cur, article_insert_query, article_values)
        retrieved_article_ids = cur.fetchall()

        inserted_article_ids = {
            row['article_url']: row['article_id'] for row in retrieved_article_ids}

        self.__db_connection.commit()
        cur.close()
        return inserted_article_ids

    def _insert_article_topic(self, inserted_article_ids: dict[str:int]):
        '''Inserts articles topics into article table'''

        article_topic_insert_query = '''INSERT INTO article_topic
        (article_id, topic_id, article_topic_positive_sentiment,
          article_topic_negative_sentiment, article_topic_neutral_sentiment,
            article_topic_compound_sentiment) VALUES (%s, %s, %s, %s, %s, %s);'''
        cur = self._create_cursor()

        article_topic_insert_values = []
        topic_id_dict = self._get_topic_id()
        for article in self.articles:
            article_id = inserted_article_ids[article.get_url()]
            for topic_analysis in article.get_topic_analyses():
                row = (article_id, topic_id_dict[topic_analysis.get_topic_name(
                )], *topic_analysis.get_sentiments())
                article_topic_insert_values.append(row)

        cur.executemany(article_topic_insert_query,
                        article_topic_insert_values)
        self.__db_connection.commit()
        cur.close()

    def insert_into_database(self):
        '''Inserts the relevant information about the article into the database'''
        inserted_article_id_dict = self._insert_article()
        self._insert_article_topic(inserted_article_id_dict)
        self.close_connection()

    def close_connection(self) -> None:
        '''Closes the database connection.'''
        if self.__db_connection:
            self.__db_connection.close()


if __name__ == "__main__":
    start = time.time()
    extracted = ExpressRSSFeedExtractor(
        ["https://www.express.co.uk/posts/rss/139/politics",]).extract_feeds()
    print("step1")
    guardian_articles = ArticleFactory(extracted).generate_articles()
    print("step2")
    TextAnalyser(guardian_articles).extract_topics()
    print("step3")
    TextAnalyser(guardian_articles).perform_article_body_analysis()
    print("step4")
    TextAnalyser(guardian_articles).perform_topic_analysis()
    DatabaseManager(guardian_articles).insert_into_database()
    end = time.time()
    elapsed = end - start
    print(f"Elapsed time: {elapsed:.2f} seconds")
