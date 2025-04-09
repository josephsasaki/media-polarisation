from dotenv import load_dotenv
import psycopg2.extras
from psycopg2.extensions import connection
import psycopg2
import os
from models import Article


class DatabaseManager:
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

    def _create_cursor(self):
        '''Creates a new cursor for the connection'''
        return self.__db_connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)

    def _get_outlet_id(self):
        '''Retrieves the the id of the news outlet'''
        cur = self._create_cursor()
        cur.execute('SELECT news_outlet_id, news_outlet_name FROM news_outlet')
        outlet_ids = cur.fetchall()
        cur.close()
        outlet_ids_dict = {row['news_outlet_name']: row['news_outlet_id']
                           for row in outlet_ids}
        print(outlet_ids_dict)
        return outlet_ids_dict

    def _get_topic_id(self):
        '''Retrieves the the id of the news outlet'''
        cur = self._create_cursor()
        cur.execute('SELECT topic_id, topic_name FROM topic')
        topic_ids = cur.fetchall()
        cur.close()
        topic_dict = {row['topic_name']: row['topic_id']
                      for row in topic_ids}
        return topic_dict

    def _get_formatted_article_values(self, article: list[str, float]) -> list[int, str, float]:
        '''returns the article values ready for insertion'''
        article_values = article.get_insert_values()
        outlet_id = self.outlet_ids[article_values[0]]
        article_values[0] = outlet_id
        return article_values

    def _insert_article(self):
        '''Inserts articles into article table'''
        cur = self._create_cursor()
        article_values = []
        for article in self.articles:
            article_values.append(tuple(self._get_formatted_article_values(
                article)))
        insert_query = '''INSERT INTO article (news_outlet_id, article_headline, article_url, article_published_date,
          article_subjectivity, article_polarity) VALUES (%s, %s, %s, %s, %s, %s)'''
        cur.executemany(insert_query, article_values)
        self.__db_connection.commit()
        cur.close()

    def close_connection(self) -> None:
        '''Closes the database connection.'''
        if self.__db_connection:
            self.__db_connection.close()


if __name__ == "__main__":
    articles = [Article("The Guardian", "Test Headline", "www.test.co.uk",
                        "Wed, 09 Apr 2025 15:07:33", "Breaking news: this is a test"), Article("The Guardian", "Test 2 Headline", "www.test2.co.uk",
                                                                                               "Wed, 09 Apr 2025 18:07:33", "Breaking news: this is a test2")]
    DatabaseManager(articles)._insert_article()
