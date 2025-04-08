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

    def __init__(self, feed_url: str):
        self.feed_url = feed_url
        self.articles = self.parse()

    def link_extractor(self, link):
        '''Extracts the raw article body from the inputted link'''
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()  # Ensure successful status code
            return response
        except requests.Timeout:
            print(f"Request to {link} timed out.")
            return None
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def article_body(self, response, link) -> str:
        """Scapes the article body of the given link"""

        if response.status_code == 200:

            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            text_body = ''
            if 'guardian' in link:
                paragraphs = soup.find_all('p', class_="dcr-16w5gq9")
                text_body = ''.join(p.get_text() for p in paragraphs)
                if not text_body.strip():
                    return None
            else:
                divs = [div for div in soup.find_all('div') if div.get('class') == [
                    'text-description']]
                for div in divs:
                    paragraphs = div.find_all('p')
                text_body += ''.join(p.get_text() for p in paragraphs)
            return text_body
        print(
            f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    def parse(self):
        """Parses the given rss feed"""
        combined_article = []
        print(self.feed_url)
        feed = feedparser.parse(self.feed_url)

        if not feed.entries:
            print("No articles found.")
            return None

        print(len(feed.entries))
        for entry in feed.entries:
            link = entry.get('link', '')
            response = self.link_extractor(link)
            body = self.article_body(response, link)
            if body:
                combined_article.append((entry, body))
        return combined_article


class NewsOutlet:
    '''The NewsOutlet class contains rss feed links of interest and extracts them
      using the RSSFeedExtractor class'''

    def __init__(self, rss_feeds: list[str]):
        self.rss_feeds = rss_feeds
        self.feeds = self.feed_extract()

    def feed_extract(self):
        '''Extracts the lists of rss feeds'''
        return [RSSFeedExtractor(feed) for feed in self.rss_feeds]


if __name__ == "__main__":
    guardian = ["https://www.theguardian.com/politics/rss",
                "https://www.theguardian.com/us-news/us-politics/rss",
                "https://www.theguardian.com/world/rss"]
    express = ["https://www.express.co.uk/posts/rss/139/politics",
               "https://www.express.co.uk/posts/rss/198/us",
               "https://www.express.co.uk/posts/rss/78/world"]

    print(NewsOutlet(express))
    print(NewsOutlet(guardian))
