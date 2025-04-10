

from extract import GuardianRSSFeedExtractor, ExpressRSSFeedExtractor
from transform import ArticleFactory, TextAnalyser
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

    def run(self):
        '''Run entire news scraper pipeline.'''
        all_articles = []
        for extractor in self.__rss_feed_extractors:
            feed = extractor.extract_feeds()
            all_articles.extend(feed)

        article_factory = ArticleFactory(all_articles)
        articles = article_factory.generate_articles()

        text_analyser = TextAnalyser(articles)
        text_analyser.extract_topics()
        text_analyser.perform_article_body_analysis()
        text_analyser.perform_topic_analysis()


if __name__ == "__main__":
    NewsScraper().run()
