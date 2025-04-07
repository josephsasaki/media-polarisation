import feedparser
import pandas as pd
from typing import List


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

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'id': self.id,
            'summary': self.summary,
            'link': self.link,
            'published': self.published,
            'author': self.author,
            'tags': self.tags,
            'updated': self.updated,
        }


class RSSFeedParser:
    def __init__(self, feed_url: str):
        self.feed_url = feed_url
        self.articles = self.parse()

    def parse(self):
        feed = feedparser.parse(self.feed_url)
        if not feed.entries:
            print("No articles found.")
            return
        return [NewsArticle(entry) for entry in feed.entries]

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([article.to_dict() for article in self.articles])


if __name__ == "__main__":
    guardian_feed_url = "https://www.theguardian.com/politics/rss"
    express_feed_url = "https://www.express.co.uk/posts/rss/139/politics"
    parser = RSSFeedParser("https://www.theguardian.com/politics/rss")
    df = parser.to_dataframe()
    print(df.head())


# def news_dataframe() -> pd.DataFrame:
#     """Creates a dataframe for the news feed"""
#     news_columns = {
#         'title': [],
#         'id': [],
#         'summary': [],
#         'link': [],
#         'published': [],
#         'author': [],
#         'tags': [],
#         'published': [],
#         'updated': []}
#     return pd.DataFrame(news_columns)


# def rss_extractor(feed_url: str) -> pd.DataFrame:
#     """Extracts a specific rss feed"""
#     news_df = news_dataframe()
#     feed = feedparser.parse(feed_url)
#     print(feed.entries[0].keys())
#     for entry in feed.entries:
#         new_row = {
#             'title': [entry.title][0],
#             'id': [entry.id][0],
#             'summary': [entry.summary_detail['value']][0],
#             'link': [entry.link][0],
#             'published': [entry.published][0],
#             'author': [entry.author][0],
#             'tags': [entry.tags][0],
#             'published': [entry.published][0],
#             'updated': [entry.updated][0]}
#         news_df = pd.concat(
#             [news_df, pd.DataFrame([new_row])], ignore_index=True)
#     return news_df
