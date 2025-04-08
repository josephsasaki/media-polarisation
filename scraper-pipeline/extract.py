'''
The extract section of the first data pipeline. The source of the data is the Guardians and 
The Daily Express' respective RSS Feeds. The parsed data for each article is stored in a tuple 
alongside the articles main body of text, the tuples are stored in a python list
'''
import feedparser
from bs4 import BeautifulSoup
import requests


class RSSFeedExtractor:
    '''The RSSFeed class extracts all articles on the inputted rss url,
      it also scrapes each individual article's body of content'''

    def __init__(self, rss_feeds: list[str]):
        self.rss_feeds = rss_feeds

    def _body_extractor(self, link):
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

    def body_formatter(self, response) -> str:
        """Formats the inputted raw article body response"""
        return response

    def _rss_parser(self, feed_url):
        """Parses the given rss feed"""
        combined_article = []
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            print("No articles found.")
            return None

        for entry in feed.entries:
            required_entry = {}
            link = entry.get('link', '')
            response = self._body_extractor(link)
            body = self.body_formatter(response)
            required_entry['title'] = entry.get('title', '')
            required_entry['link'] = link
            required_entry['published'] = entry.get('published', '')
            if body:
                combined_article.append((required_entry, body))
        return combined_article

    def extract_feeds(self):
        '''Extracts the lists of rss feeds'''
        combined_feeds = []
        for feed in self.rss_feeds:
            combined_feeds.extend(self._rss_parser(feed))
        return combined_feeds


class GuardianRSSFeedExtractor(RSSFeedExtractor):
    '''The GuardianRSSFeedExtractor class extracts all articles from the inputted Guardian rss url,
      it also scrapes each individual article's body of content'''

    def body_formatter(self, response) -> str:
        """Scapes the article body of the given link"""
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


class ExpressRSSFeedExtractor(RSSFeedExtractor):
    '''The ExpressRSSFeedExtractor class extracts all articles from the inputted
      Daily Express rss url, it also scrapes each individual article's body of content'''

    def body_formatter(self, response) -> str:
        """Scapes the article body of the given link"""

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


if __name__ == "__main__":
    guardian = ["https://www.theguardian.com/politics/rss",
                "https://www.theguardian.com/us-news/us-politics/rss",
                "https://www.theguardian.com/world/rss"]
    express = ["https://www.express.co.uk/posts/rss/139/politics",
               "https://www.express.co.uk/posts/rss/198/us",
               "https://www.express.co.uk/posts/rss/78/world"]

    print(GuardianRSSFeedExtractor(guardian).extract_feeds())
    print(ExpressRSSFeedExtractor(express).extract_feeds())
