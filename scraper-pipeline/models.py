'''
    Script defining the models relevant for the scraper pipeline.
'''

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    '''Dataclass representing an article.'''
    __news_outlet: str
    __headline: str
    __url: str
    __published_date: datetime
    __subjectivity: float
    __polarity: float

    def get_insert_values(self) -> tuple:
        '''Get the article values required for inserting into database.'''
        return (
            self.__news_outlet,
            self.__headline,
            self.__url,
            self.__published_date,
            self.__subjectivity,
            self.__polarity
        )


@dataclass
class Topic:
    '''Dataclass representing a topic.'''
    __topic_name: str

    def get_insert_values(self) -> tuple:
        '''Get the topic values required for inserting into database.'''
        return (self.__topic_name, )


@dataclass
class ArticleTopic:
    '''Dataclass representing the analysis of a topic within an article.'''
    __article: Article
    __topic: Topic
    __positive_sentiment: float
    __negative_sentiment: float
    __neutral_sentiment: float
    __compound_sentiment: float

    def get_insert_values(self) -> tuple:
        '''Get the article-topic values for inserting into database.'''
        return (
            self.__article,
            self.__topic,
            self.__positive_sentiment,
            self.__negative_sentiment,
            self.__neutral_sentiment,
            self.__compound_sentiment,
        )
