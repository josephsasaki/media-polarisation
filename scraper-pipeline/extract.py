import feedparser
import pandas as pd
from bs4 import BeautifulSoup
import requests


class NewsArticle:
    def __init__(self, entry: dict):
        self.title = entry.get('title', '')
        self.id = entry.get('id', '')
        self.summary = entry.get('summary_detail', {}).get('value', '')
        self.link = entry.get('link', '')
        self.published = entry.get('published', '')
        self.updated = entry.get('updated', '')
        self.author = entry.get('author', '')
        self.tags = [tag['term'] for tag in entry.get('tags', [])]
        self.content = self.article_body()

    def to_dict(self) -> dict:
        """Returns a dictionary to form the the columns in the dataframe"""
        return {
            'title': self.title,
            'id': self.id,
            'summary': self.summary,
            'link': self.link,
            'published': self.published,
            'author': self.author,
            'tags': self.tags,
            'updated': self.updated,
            'content': self.content
        }

    def article_body(self) -> str:
        """Scapes the articles body of content"""
        response = requests.get(self.link)

        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            text_body = ''
            if 'guardian' in self.link:
                paragraphs = soup.find_all('p', class_="dcr-16w5gq9")
                text_body = ''.join(p.get_text() for p in paragraphs)
                if not text_body.strip():
                    return None
            else:
                divs = [
                    div for div in soup.find_all('div')
                    if div.get('class') == ['text-description']
                ]
                for div in divs:
                    paragraphs = div.find_all('p')
                    text_body += ''.join(p.get_text() for p in paragraphs)
            return text_body
        else:
            print(
                f"Failed to retrieve the page. Status code: {response.status_code}")


class RSSFeed:
    def __init__(self, feed_url: str):
        self.feed_url = feed_url
        self.articles = self.parse()

    def parse(self):
        feed = feedparser.parse(self.feed_url)
        if not feed.entries:
            print("No articles found.")
            return
        # return NewsArticle(feed.entries[0])
        return [NewsArticle(entry) for entry in feed.entries]

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([article.to_dict() for article in self.articles])


if __name__ == "__main__":
    guardian_feed_url = "https://www.theguardian.com/politics/rss"
    express_feed_url = "https://www.express.co.uk/posts/rss/139/politics"
    guardian = RSSFeed(guardian_feed_url)
    express = RSSFeed(express_feed_url)

    guardian_df = guardian.to_dataframe()
    express_df = express.to_dataframe()
    express_df.to_csv("express.csv", index=False)
    guardian_df.to_csv("guardian.csv", index=False)
