'''
    Script defining the models relevant for the scraper pipeline.
'''

from datetime import datetime


class Article:
    '''Class representing an article.'''

    def __init__(self, news_outlet: str, headline: str, url: str,
                 published_date: datetime, subjectivity: float, polarity: float):
        '''Initialise the article object.'''
        self.__news_outlet = news_outlet
        self.__headline = headline
        self.__url = url
        self.__published_date = published_date
        self.__subjectivity = subjectivity
        self.__polarity = polarity


class Topic:
    '''Class representing a topic.'''

    def __init__(self, topic_name: str):
        '''Initialise the topic object'''
        self.__topic_name = topic_name


class ArticleTopic:
    '''Class representing the analysis of a topic within an article.'''

    def __init__(self, article: Article, topic: Topic, positive_sentiment: float,
                 negative_sentiment: float, neutral_sentiment: float, compound_sentiment: float):
        '''Initialise an article-topic object.'''
        self.__article = article
        self.__topic = topic
        self.__positive_sentiment = positive_sentiment
        self.__negative_sentiment = negative_sentiment
        self.__neutral_sentiment = neutral_sentiment
        self.__compound_sentiment = compound_sentiment
