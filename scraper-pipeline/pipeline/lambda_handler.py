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
