'''
    Script for converting the raw, RSS feed article data into cleaned objects.
'''

from openai import OpenAI
from models import ...


class DataTransformer:
    '''Class for transforming the raw RSS feed articles into objects.'''

    def _transform(self, raw_data: list[tuple[dict, str]]):
        '''Instantiate the articles, topics and article-topics objects from the
        raw data.'''
        for article_data in raw_data:
            meta_data = article_data[0]
            article_text = article_data[1]

    def __init__(self, raw_data: list[tuple[dict, str]]):
        '''Instantiate the DataTransformer with the raw, unclean data.'''
        self.__raw_data = raw_data
