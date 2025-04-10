'''
    Script for converting the raw, RSS feed article data into cleaned objects.
'''
import json
from datetime import datetime
import time
from openai import OpenAI
from dotenv import load_dotenv
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from models import Article, TopicAnalysis
from extract import GuardianRSSFeedExtractor, ExpressRSSFeedExtractor


load_dotenv()
# pylint: disable=too-few-public-methods


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
            published_date = None
            date_str = meta_data.get('published')
            for date_type in ('%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S %Z'):
                try:
                    published_date = datetime.strptime(date_str, date_type)
                    break
                except (ValueError, TypeError):
                    continue
            article = Article(
                news_outlet=meta_data.get('news_outlet'),
                headline=meta_data.get('title'),
                url=meta_data.get('link'),
                published_date=published_date,
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
        directly link to the topic. Do not include ```json

        Here is the article content:
        {article_body}
    '''

    def __init__(self, articles: list[Article]):
        '''Instantiate the TextAnalyser object with the list of articles to analyse.'''
        self.__articles = articles
        self.__client = OpenAI()
        self.__sentiment_analyzer = SentimentIntensityAnalyzer()

    def extract_topics(self) -> None:
        '''For each article, extract the relevant topics and assign to the article's topics list.'''
        for article in self.__articles:
            print("article_loop")
            response = self.__client.responses.create(
                model=self.GPT_MODEL,
                input=self.GPT_PROMPT.format(article_body=article.get_body())
            )

            topics_data = json.loads(response.output_text)

            topic_analyses = []
            for topic in topics_data:
                topic_analysis = TopicAnalysis(
                    topic_name=topic.get('topic_name'),
                    key_terms=topic.get('key_terms')
                )
                # print(topic_analysis.get_topic_name())
                topic_analyses.append(topic_analysis)
            article.set_topics_analyses(topic_analyses)
            # print("-------------new article-------------")

    # def check_validity_of_topics():
    # checking if the key_terms for each topic actually show up in the text, and they are relevant
    # NLP library for this

    def perform_topic_analysis(self) -> None:
        '''For each article, iterate through it's topics and perform the NLP analysis on the 
        sentiment of each topic within the article.'''
        for article in self.__articles:
            body = article.get_body()
            sentences = nltk.sent_tokenize(body)
            for topic in article.get_topic_analyses():
                key_terms = topic.get_key_terms()

                related_sentences = [
                    sentence for sentence in sentences
                    if any(term.lower() in sentence.lower() for term in key_terms)
                ]

                if related_sentences:
                    context_text = " ".join(related_sentences)
                    sentiment_scores = self.__sentiment_analyzer.polarity_scores(
                        context_text)

                    topic.set_sentiments(
                        positive=sentiment_scores['pos'],
                        neutral=sentiment_scores['neu'],
                        negative=sentiment_scores['neg'],
                        compound=sentiment_scores['compound'],
                    )

    def perform_article_body_analysis(self) -> None:
        '''Performs the NLP sentiment analysis on the article body'''
        for article in self.__articles:
            body = article.get_body()
            blob = TextBlob(body)
            subjectivity = blob.sentiment.subjectivity
            polarity = blob.sentiment.polarity

            sentiment_scores = self.__sentiment_analyzer.polarity_scores(
                body)
            article.set_polarity(polarity)
            article.set_subjectivity(subjectivity)
            article.set_sentiments(
                sentiment_scores['pos'],
                sentiment_scores['neu'],
                sentiment_scores['neg'],
                sentiment_scores['compound'])


if __name__ == "__main__":
    start = time.time()
    extracted = GuardianRSSFeedExtractor(
        ["https://www.theguardian.com/politics/rss",]).extract_feeds()
    # extracted = ExpressRSSFeedExtractor(
    #     ["https://www.express.co.uk/posts/rss/78/world",]).extract_feeds()

    print("step1")
    guardian_articles = ArticleFactory(extracted).generate_articles()
    print("step2")
    TextAnalyser(guardian_articles).extract_topics()
    print("step3")
    TextAnalyser(guardian_articles).perform_article_body_analysis()
    print("step4")
    TextAnalyser(guardian_articles).perform_topic_analysis()
    for item in guardian_articles:
        print(item.get_article_heading())
        print(f"subjectivity : {item.get_subjectivity()}")
        print(f"polarity: {item.get_polarity()}")
        print(item.get_sentiments())
        for topic_analyses in item.get_topic_analyses():
            print(f"topic: {topic_analyses.get_topic_name()}")
            print(topic_analyses.get_sentiments())

    end = time.time()
    elapsed = end - start
    print(f"Elapsed time: {elapsed:.2f} seconds")
