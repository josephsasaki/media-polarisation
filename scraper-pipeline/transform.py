'''
    Script for converting the raw, RSS feed article data into cleaned objects.
'''

import json
from datetime import datetime
from openai import OpenAI
from models import Article, TopicAnalysis


class ArticleFactory:
    '''Class for transforming the raw RSS feed articles into objects.'''

    def __init__(self, raw_data: list[tuple[dict, str]]):
        '''Instantiate the DataTransformer with the raw, unclean data.'''
        self.__raw_data = raw_data

    def generate_articles(self) -> list[Article]:
        '''Instantiate the articles from the raw data.'''
        articles = []
        for article_data in self.__raw_data:
            meta_data: dict = article_data[0]
            article_text: str = article_data[1]
            article = Article(
                news_outlet=meta_data.get('news_outlet'),
                headline=meta_data.get('title'),
                url=meta_data.get('link'),
                published_date=datetime.strptime(meta_data.get(
                    'published'), '%a, %d %b %Y %H:%M:%S %z'),
                body=article_text,
            )
            articles.append(article)
        return articles


class TextAnalyser:
    '''Class for performing text analysis on articles.'''

    GPT_MODEL = 'gpt-4o-mini'
    GPT_PROMPT = '''
        Extract the top 5 overarching topics from the following article. Please provide these
        topics in as few words as possible e.g. immigration, Donald Trump, US tariffs. I should 
        expect the outputs to be, in general, 1 word long.  
       
        Please provide a JSON list, where each element is a dictionary with two keys: topic_name
        and key_terms. The key_terms key should correspond to a list of words found in the article which
        directly link to the topic. 
        
        An example output would be as follows:
        [
            {
                "topic_name": "Immigration",
                "key_terms": ["immigrants", "immigration", "deportation"]
            },
            {
                "topic_name": "Donald Trump",
                "key_terms": ["Donald Trump", "Trump", "US President"]
            }
        ]

        Here is the article content:
        {article_body}
    '''

    def __init__(self, articles: list[Article]):
        '''Instantiate the TextAnalyser object with the list of articles to analyse.'''
        self.__articles = articles
        self.__client = OpenAI()

    def extract_topics(self) -> None:
        '''For each article, extract the relevant topics and assign to the article's topics list.'''
        for article in self.__articles:
            response = self.__client.responses.create(
                model=self.GPT_MODEL,
                input=self.GPT_PROMPT.format(article_body=article.get_body()),
            )
            topics_data = json.loads(response.output_text)
            topic_analyses = []
            for topic in topics_data:
                topic_analysis = TopicAnalysis(
                    topic_name=topic.get('topic_name'),
                    key_terms=topic.get('key_terms')
                )
                topic_analyses.append(topic_analysis)
            article.set_topics_analyses(topic_analyses)

    # def check_validity_of_topics():
    # checking if the key_terms for each topic actually show up in the text, and they are relevant
    # NLP library for this

    def perform_topic_analysis(self) -> None:
        '''For each article, iterate through it's topics and perform the NLP analysis on the 
        sentiment of each topic within the article.'''
        for article in self.__articles:
            for topic in article.get_topic_analyses():

                # TODO: perform sentiment analysis
                # article.get_body()
                # topic.get_key_terms()

                topic.set_sentiments(
                    positive=...,
                    neutral=...,
                    negative=...,
                    compound=...,
                )

    def perform_article_body_analysis(self) -> None:
        ''''''
        pass
