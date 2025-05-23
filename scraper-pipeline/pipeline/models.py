'''
    Script defining the models relevant for the scraper pipeline.
'''

from datetime import datetime


class TopicAnalysis:
    '''Class representing an article's topic and corresponding analysis for the topic.'''

    def __init__(self, topic_name: str, key_terms: list[str]):
        self.__topic_name = topic_name
        self.__key_terms = key_terms
        self.__positive_sentiment = None
        self.__neutral_sentiment = None
        self.__negative_sentiment = None
        self.__compound_sentiment = None

    def set_sentiments(self, positive: float, neutral: float, negative: float, compound: float):
        '''Set the sentiment values of a topic.'''
        self.__positive_sentiment = positive
        self.__neutral_sentiment = neutral
        self.__negative_sentiment = negative
        self.__compound_sentiment = compound

    def get_topic_name(self) -> str:
        '''Getter for the topic name.'''
        return self.__topic_name

    def get_key_terms(self) -> list[str]:
        '''Getter for the key terms.'''
        return self.__key_terms

    def get_sentiments(self) -> tuple[float]:
        '''Getter for the sentiment values.'''
        return (
            self.__positive_sentiment,
            self.__neutral_sentiment,
            self.__negative_sentiment,
            self.__compound_sentiment,
        )


class Article:
    '''Class representing an article.'''

    def __init__(self, news_outlet: str, headline: str, url: str,
                 published_date: datetime, body: str):
        '''Instantiate the article object'''
        self.__news_outlet = news_outlet
        self.__headline = headline
        self.__url = url
        self.__published_date = published_date
        self.__body = body
        self.__topic_analyses = None
        self.__subjectivity = None
        self.__polarity = None
        self.__positive_sentiment = None
        self.__neutral_sentiment = None
        self.__negative_sentiment = None
        self.__compound_sentiment = None
        self.__article_id = None

    def get_body(self):
        '''Getter for the article text body.'''
        return self.__body

    def set_topics_analyses(self, topics_analyses: list[TopicAnalysis]):
        '''Set the list of topics analyses objects related to the article.'''
        self.__topic_analyses = topics_analyses

    def get_topic_analyses(self) -> list[TopicAnalysis]:
        '''Getter for the topic analyses.'''
        return self.__topic_analyses

    def set_subjectivity(self, subjectivity: float) -> None:
        '''Sets the subjectivity of the article.'''
        self.__subjectivity = subjectivity

    def set_polarity(self, polarity: float) -> None:
        '''Sets the subjectivity of the article.'''
        self.__polarity = polarity

    def set_sentiments(self, positive: float, neutral: float, negative: float, compound: float):
        '''Set the sentiment values of an article.'''
        self.__positive_sentiment = positive
        self.__neutral_sentiment = neutral
        self.__negative_sentiment = negative
        self.__compound_sentiment = compound

    def set_id(self, database_id: int) -> None:
        '''Set the article's database primary id.'''
        self.__article_id = database_id

    def get_insert_values(self, news_outlet_id_map: dict) -> tuple:
        '''Get the article values required for inserting into database.'''
        return [
            news_outlet_id_map.get(self.__news_outlet),
            self.__headline,
            self.__url,
            self.__published_date,
            self.__subjectivity,
            self.__polarity,
            self.__positive_sentiment,
            self.__neutral_sentiment,
            self.__negative_sentiment,
            self.__compound_sentiment,
        ]

    def get_topic_analyses_insert_values(self, topic_id_map: dict) -> list[tuple]:
        '''Get the topic analyses values required for inserting into the database.'''
        insert_values = []
        for topic_analysis in self.__topic_analyses:
            insert_values.append((
                self.__article_id,
                topic_id_map[topic_analysis.get_topic_name()],
                *topic_analysis.get_sentiments(),
            ))
        return insert_values
