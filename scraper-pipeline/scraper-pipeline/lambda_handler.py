'''
    Event handler function for the AWS Lambda.
'''

from dotenv import load_dotenv
from scraper import NewsScraper


def lambda_handler(event, context=None):
    load_dotenv(override=True)
    NewsScraper(
        guardian_rss_feed_urls=event['guardian'],
        express_rss_feed_urls=event['express'],
    ).run()


{
    "guardian": [
        "https://www.theguardian.com/politics/rss",
        "https://www.theguardian.com/us-news/us-politics/rss",
        "https://www.theguardian.com/world/rss"
    ],
    "express": [
        "https://www.express.co.uk/posts/rss/139/politics",
        "https://www.express.co.uk/posts/rss/198/us",
        "https://www.express.co.uk/posts/rss/78/world"
    ]
}
