'''
    Script for converting the raw, RSS feed article data into cleaned objects.
'''
from extract import GuardianRSSFeedExtractor, ExpressRSSFeedExtractor
from models import Article
from datetime import datetime
import time


class ArticleFactory:
    # pylint: disable=too-few-public-methods
    '''Class for transforming the raw RSS feed articles into objects.'''

    def __init__(self, raw_data: list[tuple[dict, str]], existing_urls: list[str]):
        '''Instantiate the DataTransformer with the raw, unclean data.'''
        self.__raw_data = raw_data
        self.__existing_urls = existing_urls

    def _clean_date(self, date_str: str) -> datetime:
        '''Given a date string, convert to a datetime object. Different news outlets
        have different date formats.'''
        date_format_options = {
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S %Z',
        }
        for date_format in date_format_options:
            try:
                date_obj = datetime.strptime(date_str, date_format)
                return date_obj
            except (ValueError, TypeError):
                continue
        raise ValueError("Article has date with unrecognised format.")

    def _check_is_new_url(self, url: str) -> None:
        '''Check the url is new, otherwise raise an error.'''
        if url in self.__existing_urls:
            raise ValueError("Article url already exists in database.")
        return url

    def generate_articles(self) -> list[Article]:
        '''Instantiate the articles from the raw data.'''
        articles = []
        for article_data in self.__raw_data:
            try:
                url = self._check_is_new_url(article_data['url'])
                article = Article(
                    news_outlet=article_data['news_outlet'],
                    headline=article_data['headline'],
                    url=url,
                    published_date=self._clean_date(
                        article_data['published_date']),
                    body=article_data['body'],
                )
                articles.append(article)
                # Add url in case of duplicate within batch
                self.__existing_urls.append(url)
            except ValueError:
                continue
        return articles
