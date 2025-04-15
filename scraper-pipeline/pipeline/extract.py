'''
    The extract section of the first data pipeline. The source of the data is the Guardians and 
    The Daily Express' respective RSS Feeds. The parsed data for each article is stored in a tuple 
    alongside the articles main body of text, the tuples are stored in a python list
'''

from abc import ABC, abstractmethod
import feedparser
from bs4 import BeautifulSoup
import requests

# pylint: disable=too-few-public-methods


class RSSFeedExtractor(ABC):
    '''The RSSFeed class extracts all articles on the inputted rss url,
      it also scrapes each individual article's body of content.'''

    def __init__(self, rss_feeds: list[str]):
        self.rss_feeds = rss_feeds

    @abstractmethod
    def _get_news_outlet(self) -> str:
        '''Returns the name of the outlet being extracted from. This must be 
        overridden by child classes for each news outlet.'''

    @abstractmethod
    def _body_formatter(self, html_content: str) -> str:
        '''Formats the inputted raw article body response. The handling of this method
        depends on the individual news outlet, so this method should be overridden.'''

    def _body_extractor(self, url: str) -> requests.Response:
        '''Extracts the raw article body from the inputted url.'''
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                text_body = self._body_formatter(response.text)
                if not text_body.strip():
                    return None
                return text_body
            print(
                f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
        except requests.Timeout:
            print(f"Request to {url} timed out.")
            return None
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def _rss_parser(self, feed_url: str) -> list[dict]:
        '''Parses the given RSS feed, and returns complete raw data for each article.'''
        combined_article = []
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            # extract the required variables from the feedparser
            headline = entry.get('title', '')
            url = entry.get('link', '')
            published_date = entry.get('published', '')
            news_outlet = self._get_news_outlet()
            # check the url is present (if not, skip article)
            if url is None:
                continue
            # attempt to extract body of article from url
            body = self._body_extractor(url)
            # check the body was retrieved (if not, skip article)
            if body is None:
                continue
            # construct the dictionary containing the raw data
            required_entry = {
                'headline': headline,
                'url': url,
                'published_date': published_date,
                'news_outlet': news_outlet,
                'body': body,
            }
            combined_article.append(required_entry)
        return combined_article

    def extract_feeds(self) -> list[dict]:
        '''Extracts the article data from each feed and combine together.'''
        combined_feeds = []
        for feed in self.rss_feeds:
            combined_feeds.extend(self._rss_parser(feed))
        return combined_feeds


class GuardianRSSFeedExtractor(RSSFeedExtractor):
    '''The GuardianRSSFeedExtractor class extracts all articles from the inputted Guardian rss url,
      it also scrapes each individual article's body of content'''

    def _body_formatter(self, html_content: str) -> str:
        '''Given the html content of a Guardian article, the relevant article text is extracted.'''
        soup = BeautifulSoup(html_content, 'html.parser')
        paragraphs = soup.find_all('p', class_="dcr-16w5gq9")
        text_body = ''.join(p.get_text() for p in paragraphs)
        return text_body

    def _get_news_outlet(self) -> str:
        '''Returns the name of the outlet being extracted from.'''
        return "The Guardian"


class ExpressRSSFeedExtractor(RSSFeedExtractor):
    '''The ExpressRSSFeedExtractor class extracts all articles from the inputted
      Daily Express rss url, it also scrapes each individual article's body of content'''

    def _body_formatter(self, html_content: str) -> str:
        '''Given the html content of an Express article, the relevant article text is extracted.'''
        soup = BeautifulSoup(html_content, 'html.parser')
        text_body = ''
        divs = [div for div in soup.find_all('div') if div.get('class') == [
                'text-description']]
        for div in divs:
            paragraphs = div.find_all('p')
            text_body += ''.join(p.get_text() for p in paragraphs)
        return text_body

    def _get_news_outlet(self) -> str:
        '''Returns the name of the outlet being extracted from.'''
        return "Daily Express"
