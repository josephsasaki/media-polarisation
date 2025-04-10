

from dotenv import load_dotenv
from extract import GuardianRSSFeedExtractor, ExpressRSSFeedExtractor
from transform import ArticleFactory
from analysis import TextAnalyser
from load import DatabaseManager


class NewsScraper:
    '''Class containing high-level methods for news scraper pipeline.'''

    def __init__(self):
        self.__rss_feed_extractors = [
            GuardianRSSFeedExtractor([
                "https://www.theguardian.com/politics/rss",
            ]),
            ExpressRSSFeedExtractor([
                "https://www.express.co.uk/posts/rss/78/world",
            ]),
        ]
        self.__db_manager = DatabaseManager()
        self.__text_analyser = TextAnalyser(
            valid_topics=self.__db_manager.get_valid_topics()
        )

    def run(self):
        '''Run entire news scraper pipeline.'''
        # EXTRACT
        all_articles = []
        for extractor in self.__rss_feed_extractors:
            feed = extractor.extract_feeds()
            all_articles.extend(feed)
        # TRANSFORM
        article_factory = ArticleFactory(
            raw_data=all_articles,
            existing_urls=self.__db_manager.get_article_urls()
        )
        articles = article_factory.generate_articles()
        # ANALYSIS
        self.__text_analyser.extract_topics(articles)
        self.__text_analyser.perform_topic_analyses(articles)
        self.__text_analyser.perform_body_analyses(articles)
        # LOAD
        self.__db_manager.insert_into_database(articles)
        self.__db_manager.close_connection()


if __name__ == "__main__":
    load_dotenv(override=True)
    NewsScraper().run()
