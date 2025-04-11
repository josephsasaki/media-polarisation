'''
    Script containing the high-level class NewsScraper for running the entire 
    data pipeline. 
'''

from extract import GuardianRSSFeedExtractor, ExpressRSSFeedExtractor
from transform import ArticleFactory
from analysis import TextAnalyser
from load import DatabaseManager


class NewsScraper:
    '''Class containing high-level methods for news scraper pipeline.'''

    def __init__(self,
                 guardian_rss_feed_urls: list[str] = None,
                 express_rss_feed_urls: list[str] = None):
        if guardian_rss_feed_urls is None:
            guardian_rss_feed_urls = []
        if express_rss_feed_urls is None:
            express_rss_feed_urls = []
        self.__rss_feed_extractors = [
            GuardianRSSFeedExtractor(guardian_rss_feed_urls),
            ExpressRSSFeedExtractor(express_rss_feed_urls),
        ]
        self.__db_manager = DatabaseManager()
        self.__text_analyser = TextAnalyser(
            valid_topics=self.__db_manager.get_valid_topics()
        )

    def run(self):
        '''Run entire news scraper pipeline.'''
        # EXTRACT
        try:
            print("Extracting...")
            all_articles = []
            for extractor in self.__rss_feed_extractors:
                feed = extractor.extract_feeds()
                all_articles.extend(feed)
            # TRANSFORM
            print("Transforming...")
            article_factory = ArticleFactory(
                raw_data=all_articles,
                existing_urls=self.__db_manager.get_article_urls()
            )
            articles = article_factory.generate_articles()
            # ANALYSIS
            print("Analysing...")
            self.__text_analyser.extract_topics(articles)
            self.__text_analyser.perform_topic_analyses(articles)
            self.__text_analyser.perform_body_analyses(articles)
            # LOAD
            print("Loading...")
            self.__db_manager.insert_into_database(articles)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.__db_manager.close_connection()
            print("Finished.")
