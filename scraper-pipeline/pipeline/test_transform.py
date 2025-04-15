'''
    Test the transformation process.
'''
from datetime import datetime
import pytest
from transform import ArticleFactory
from models import Article

# pylint: disable=protected-access


def test_clean_date_parses_known_formats():
    '''Test the clean date for correctly formatted dates.'''
    factory = ArticleFactory([], [])
    date_str_1 = "Wed, 10 Apr 2024 14:30:00 +0000"
    date_str_2 = "Wed, 10 Apr 2024 14:30:00 UTC"
    date_1 = factory._clean_date(date_str_1)
    date_2 = factory._clean_date(date_str_2)
    assert isinstance(date_1, datetime)
    assert isinstance(date_2, datetime)


def test_clean_date_raises_on_unknown_format():
    '''Test the clean date for incorrectly formatted dates.'''
    factory = ArticleFactory([], [])
    bad_date = "April 10, 2024 14:30"
    with pytest.raises(ValueError):
        factory._clean_date(bad_date)


def test_check_is_new_url_passes_if_new():
    '''Test check url.'''
    factory = ArticleFactory([], existing_urls=["http://url1.com"])
    assert factory._check_is_new_url("http://url2.com") == "http://url2.com"


def test_check_is_new_url_raises_if_duplicate():
    '''Test check url.'''
    factory = ArticleFactory([], existing_urls=["http://url1.com"])
    with pytest.raises(ValueError):
        factory._check_is_new_url("http://url1.com")


def test_generate_articles_filters_existing_and_malformed():
    '''Test whole process works correctly.'''
    raw_data = [
        {
            "news_outlet": "Guardian",
            "headline": "Article One",
            "url": "http://url10.com",
            "published_date": "Wed, 10 Apr 2024 14:30:00 +0000",
            "body": "Body of article one"
        },
        {
            "news_outlet": "Guardian",
            "headline": "Article One",
            "url": "http://url10.com",  # Duplicate URL within batch
            "published_date": "Wed, 10 Apr 2024 14:30:00 +0000",
            "body": "Body of article one"
        },
        {
            "news_outlet": "Express",
            "headline": "Duplicate Article",
            "url": "http://url1.com",  # Duplicate URL
            "published_date": "Wed, 10 Apr 2024 14:30:00 +0000",
            "body": "Body of article two"
        },
        {
            "news_outlet": "Express",
            "headline": "Bad Date",
            "url": "http://url3.com",
            "published_date": "10-04-2024 14:30",  # Invalid format
            "body": "Body of article three"
        },
        {
            "news_outlet": "Guardian",
            "headline": "Article Four",
            "url": "http://url4.com",
            "published_date": "Wed, 10 Apr 2024 14:30:00 UTC",
            "body": "Body of article four"
        },
    ]

    factory = ArticleFactory(raw_data, existing_urls=["http://url1.com"])
    articles = factory.generate_articles()

    assert len(articles) == 2
    assert all(isinstance(a, Article) for a in articles)
    assert articles[0].get_body() == "Body of article one"
    assert articles[1].get_body() == "Body of article four"
