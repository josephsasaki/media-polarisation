'''
The extract section of the first data pipeline. The source of the data is the Guardians and 
The Daily Express' respective RSS Feeds. The parsed data for each article is stored in a tuple 
alongside the articles main body of text, the tuples are stored in a python list
'''
import feedparser
from bs4 import BeautifulSoup
import requests

# pylint: disable=too-few-public-methods


class RSSFeedExtractor:
    '''The RSSFeed class extracts all articles on the inputted rss url,
      it also scrapes each individual article's body of content'''

    def __init__(self, rss_feeds: list[str]):
        self.rss_feeds = rss_feeds

    def _body_extractor(self, link: str) -> requests.Response:
        '''Extracts the raw article body from the inputted link'''
        try:
            response = requests.get(link, timeout=10)
            return response
        except requests.Timeout:
            print(f"Request to {link} timed out.")
            return None
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def _body_formatter(self, response: requests.Response) -> str:
        '''Formats the inputted raw article body response'''
        return f"{response}"

    def _get_news_outlet(self) -> str:
        '''Returns the name of the outlet being extracted from'''
        return "news_outlet"

    def _rss_parser(self, feed_url: requests.Response) -> list[tuple[dict, str]]:
        '''Parses the given rss feed'''
        combined_article = []
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            print("No articles found.")
            return None

        for entry in feed.entries:
            required_entry = {}
            link = entry.get('link', '')
            response = self._body_extractor(link)
            body = self._body_formatter(response)
            required_entry['title'] = entry.get('title', '')
            required_entry['link'] = link
            required_entry['published'] = entry.get('published', '')
            required_entry['news_outlet'] = self._get_news_outlet()
            if body:
                combined_article.append((required_entry, body))
        return combined_article

    def extract_feeds(self) -> list[tuple[dict, str]]:
        '''Extracts the lists of rss feeds'''
        combined_feeds = []
        for feed in self.rss_feeds:
            combined_feeds.extend(self._rss_parser(feed))
        return combined_feeds


class GuardianRSSFeedExtractor(RSSFeedExtractor):
    '''The GuardianRSSFeedExtractor class extracts all articles from the inputted Guardian rss url,
      it also scrapes each individual article's body of content'''

    def _body_formatter(self, response: requests.Response) -> str:
        '''Scapes the article body of the given link'''
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            text_body = ''

            paragraphs = soup.find_all('p', class_="dcr-16w5gq9")
            text_body = ''.join(p.get_text() for p in paragraphs)
            if not text_body.strip():
                return None
            return text_body
        print(
            f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    def _get_news_outlet(self) -> str:
        '''Returns the name of the outlet being extracted from'''
        return "The Guardian"


class ExpressRSSFeedExtractor(RSSFeedExtractor):
    '''The ExpressRSSFeedExtractor class extracts all articles from the inputted
      Daily Express rss url, it also scrapes each individual article's body of content'''

    def _body_formatter(self, response: requests.Response) -> str:
        '''Scapes the article body of the given link'''

        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            text_body = ''
            divs = [div for div in soup.find_all('div') if div.get('class') == [
                    'text-description']]
            for div in divs:
                paragraphs = div.find_all('p')
                text_body += ''.join(p.get_text() for p in paragraphs)
            return text_body
        print(
            f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    def _get_news_outlet(self) -> str:
        '''Returns the name of the outlet being extracted from'''
        return "Daily Express"
