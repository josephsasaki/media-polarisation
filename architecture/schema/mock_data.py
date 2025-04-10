# pylint: skip-file
''''
    Script for uploading mock article data to the RDS for checking the archival pipeline works.
'''

import os
from datetime import datetime, timedelta, date, time
import psycopg2
from psycopg2.extensions import connection
import random
from dotenv import dotenv_values


def daterange(start_date: date, end_date: date):
    '''Generator for a range of dates.'''
    days = int((end_date - start_date).days)
    for n in range(days):
        yield start_date + timedelta(n)


def generate_mock_articles(articles_per_day: int, start_date: datetime, end_date: datetime):
    '''Generate the values representing an article.'''
    articles = []
    for date in daterange(start_date, end_date):
        for i in range(articles_per_day):
            articles.append((
                random.randint(1, 2),
                f"Article Headline: News {i} on {date.strftime('%d/%m/%Y')}",
                f"https://news_outlet.com/{date.strftime('%Y/%m/%d')}/{i}",
                datetime.combine(date, time(hour=12, minute=0)),
                round(random.uniform(0, 1)*1000)/1000,
                round(random.uniform(0, 1)*1000)/1000,
                round(random.uniform(0, 1)*1000)/1000,
                round(random.uniform(0, 1)*1000)/1000,
                round(random.uniform(0, 1)*1000)/1000,
                round(random.uniform(-1, 1)*1000)/1000,
            ))
    return articles


def generate_mock_article_topics(articles: list[tuple], max_topic_id: int):
    '''Generate the article topics.'''
    topic_ids = list(range(1, max_topic_id+1))
    article_topics = []
    for article in articles:
        random.shuffle(topic_ids)
        article_topic_ids = topic_ids[:random.randint(1, 10)]
        for article_topic_id in article_topic_ids:
            article_topics.append((
                # article_id
                article[0],
                # topic_id
                article_topic_id,
                # article_topic_positive_sentiment
                round(random.uniform(0, 1)*1000)/1000,
                # article_topic_negative_sentiment
                round(random.uniform(0, 1)*1000)/1000,
                # article_topic_neural_sentiment
                round(random.uniform(0, 1)*1000)/1000,
                # article_topic_compound_sentiment
                round(random.uniform(-1, 1)*1000)/1000,
            ))
            article_topic_id += 1
    return article_topics


if __name__ == "__main__":
    # CONNECT TO DATABASE
    config = dotenv_values(".env")
    conn = psycopg2.connect(
        database=config['DB_NAME'],
        user=config["DB_USERNAME"],
        host=config["DB_HOST"],
        password=config["DB_PASSWORD"],
        port=config["DB_PORT"]
    )
    cur = conn.cursor()
    # GENERATE ENTRIES
    articles = generate_mock_articles(
        articles_per_day=5,
        start_date=date(year=2025, month=1, day=5),
        end_date=date(year=2025, month=1, day=9),
    )
    topics = generate_mock_topics(20)
    article_topics = generate_mock_article_topics(articles, topics)
    # CLEAR THE TABLES
    cur.execute("DELETE FROM article_topic")
    cur.execute("DELETE FROM topic")
    cur.execute("DELETE FROM article")
    # INSERT INTO THE DATABASE
    cur.executemany('''
        INSERT INTO topic
            (topic_name)
        VALUES
            (%s)
    ''', topics)
    cur.executemany('''
        INSERT INTO article
            (news_outlet_id, article_headline, article_url, 
                    article_published_date, article_subjectivity, article_polarity)
        VALUES
            (%s, %s, %s, %s, %s, %s)
    ''', articles)
    # cur.executemany('''
    #     INSERT INTO article_topic
    #         (article_topic_id, article_id, topic_id, article_topic_positive_sentiment,
    #                 article_topic_negative_sentiment, article_topic_neural_sentiment,
    #                 article_topic_compound_sentiment)
    #     OVERRIDING SYSTEM VALUE
    #     VALUES
    #         (%s, %s, %s, %s, %s, %s, %s)
    # ''', article_topics)
    conn.commit()
    conn.close()
    print("SUCCESS")
