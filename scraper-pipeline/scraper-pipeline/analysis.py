'''
    Script which defines the TextAnalyser class, used for completing sentiment analysis on
    articles.
'''

import json
from openai import OpenAI
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

from models import Article, TopicAnalysis


class TextAnalyser:
    '''Class for performing text analysis on articles.'''

    GPT_MODEL = 'gpt-4o-mini'
    GPT_PROMPT = '''
        Extract the top 5 overarching topics from the following article. Please provide these
        topics in as few words as possible e.g. immigration, Donald Trump, US tariffs. I should
        expect the outputs to be, in general, 1 word long.

        Please provide a JSON list, where each element is a dictionary with two keys: topic_name
        and key_terms. The key_terms key should correspond to a list of words found in the article which
        directly link to the topic. Do not include ```json

        The 5 overarching topics must also be contained within this list:
        {valid_topics}

        you can have less than 5 if there aren't 5 topics within the article that are also within the list

        Here is the article content:
        {article_body}
    '''

    def __init__(self, valid_topics: list[str]):
        '''Instantiate the TextAnalyser object.'''
        nltk.download('punkt_tab', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        self.__client = OpenAI()
        self.__sentiment_analyser = SentimentIntensityAnalyzer()
        self.__valid_topics = valid_topics

    def _ask_openai(self, article: Article) -> None:
        '''For each of the articles, ask OpenAI's GPT to extract topic data.
        Each article has a list of dictionaries (each representing a topic).'''
        # form prompt
        prompt = self.GPT_PROMPT.format(
            valid_topics=", ".join(self.__valid_topics),
            article_body=article.get_body(),
        )
        # ask openai
        response = self.__client.chat.completions.create(
            model=self.GPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            n=1,
        )
        # extract the response content and convert to json obj
        return json.loads(response.choices[0].message.content)

    def _validate_topics(self, topic_data: list[dict]) -> None:
        '''Filter out any topic dictionaries with invalid topics. Changes are
        made in place.'''
        return [d for d in topic_data if d['topic_name'] in self.__valid_topics]

    def _validate_key_terms(self, topic_data: list[dict], article: Article) -> list[dict]:
        '''Filter out any key terms which do not appear in the article body. If all key
        terms end up being removed, the whole topic dictionary is removed. Changes are
        made in place.'''
        valid_topic_data = []
        for topic_dict in topic_data:
            key_terms = topic_dict['key_terms']
            valid_key_terms = [
                key_term for key_term in key_terms if key_term in article.get_body()]
            if len(valid_key_terms) > 0:
                topic_dict['key_terms'] = valid_key_terms
                valid_topic_data.append(topic_dict)
        return valid_topic_data

    def _assign_topic_analysis_object(self, topic_data: list[dict], article: Article) -> None:
        '''Given the topic data, create a topic analysis object and assign to the article.'''
        topic_analyses = []
        for topic in topic_data:
            topic_analyses.append(TopicAnalysis(
                topic_name=topic.get('topic_name'),
                key_terms=topic.get('key_terms'),
            ))
        article.set_topics_analyses(topic_analyses)

    def extract_topics(self, articles: list[Article]) -> None:
        '''For each article, extract the relevant topics and assign to the article's topics list.'''
        for article in articles:
            topic_data = self._ask_openai(article)
            topic_data = self._validate_topics(topic_data)
            topic_data = self._validate_key_terms(topic_data, article)
            self._assign_topic_analysis_object(topic_data, article)

    def _perform_single_topic_analysis(self, topic_analysis: TopicAnalysis, sentences):
        '''Perform sentiment analysis for a single topic.'''
        key_terms = topic_analysis.get_key_terms()
        related_sentences = [
            sentence for sentence in sentences
            if any(term.lower() in sentence.lower() for term in key_terms)
        ]
        context_text = " ".join(related_sentences)
        sentiment_scores = self.__sentiment_analyser.polarity_scores(
            context_text)
        topic_analysis.set_sentiments(
            positive=sentiment_scores['pos'],
            neutral=sentiment_scores['neu'],
            negative=sentiment_scores['neg'],
            compound=sentiment_scores['compound'],
        )

    def perform_topic_analyses(self, articles: list[Article]) -> None:
        '''For each article, iterate through it's topics and perform the NLP analysis on the
        sentiment of each topic within the article.'''
        for article in articles:
            body = article.get_body()
            sentences = nltk.sent_tokenize(body)
            for topic_analysis in article.get_topic_analyses():
                self._perform_single_topic_analysis(topic_analysis, sentences)

    def perform_body_analyses(self, articles: list[Article]) -> None:
        '''Performs the NLP sentiment analysis on the article body.'''
        for article in articles:
            body = article.get_body()
            blob = TextBlob(body)
            subjectivity = blob.sentiment.subjectivity
            polarity = blob.sentiment.polarity
            sentiment_scores = self.__sentiment_analyser.polarity_scores(
                body)
            article.set_polarity(polarity)
            article.set_subjectivity(subjectivity)
            article.set_sentiments(
                sentiment_scores['pos'],
                sentiment_scores['neu'],
                sentiment_scores['neg'],
                sentiment_scores['compound']
            )
