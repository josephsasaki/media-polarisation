'''
    Test the models.
'''

from datetime import datetime
from models import TopicAnalysis, Article


def test_topic_analysis_initialization():
    '''Test topic analysis instantiation, as well as the getters.'''
    ta = TopicAnalysis("Climate Change", ["emissions", "carbon", "warming"])
    assert ta.get_topic_name() == "Climate Change"
    assert ta.get_key_terms() == ["emissions", "carbon", "warming"]
    assert ta.get_sentiments() == (None, None, None, None)


def test_topic_analysis_set_sentiments():
    '''Test the set_sentiment method.'''
    ta = TopicAnalysis("Economy", ["inflation", "GDP"])
    ta.set_sentiments(0.3, 0.5, 0.2, 0.1)
    assert ta.get_sentiments() == (0.3, 0.5, 0.2, 0.1)


def test_article_initialization_and_getters():
    '''Test article instantiation and the getter methods.'''
    pub_date = datetime(2024, 1, 1)
    article = Article(
        news_outlet="Guardian",
        headline="Major Climate Report Released",
        url="http://example.com/article",
        published_date=pub_date,
        body="Full article text here."
    )
    assert article.get_body() == "Full article text here."
    assert article.get_topic_analyses() is None


def test_article_setters_and_getters():
    '''Test article getters and setters.'''
    article = Article("Express", "Headline", "http://url",
                      datetime.now(), "Body")
    topics = [
        TopicAnalysis("Environment", ["pollution"]),
        TopicAnalysis("Policy", ["law"])
    ]
    article.set_topics_analyses(topics)
    assert article.get_topic_analyses() == topics

    article.set_subjectivity(0.75)
    article.set_polarity(0.2)
    article.set_sentiments(0.1, 0.6, 0.3, 0.0)
    article.set_id(42)

    news_outlet_map = {"Express": 2}
    insert_vals = article.get_insert_values(news_outlet_map)

    assert insert_vals[:3] == [2, "Headline", "http://url"]
    assert insert_vals[4:8] == [0.75, 0.2, 0.1, 0.6]
    assert insert_vals[8:] == [0.3, 0.0]


def test_article_topic_analysis_insert_values():
    '''Test the topic analysis insert values method.'''
    article = Article("Guardian", "Headline",
                      "http://url", datetime.now(), "Body")
    article.set_id(99)

    topic1 = TopicAnalysis("Climate", ["warming", "ice"])
    topic1.set_sentiments(0.2, 0.3, 0.1, 0.05)

    topic2 = TopicAnalysis("Energy", ["renewables"])
    topic2.set_sentiments(0.4, 0.4, 0.1, 0.2)

    article.set_topics_analyses([topic1, topic2])

    topic_id_map = {"Climate": 1, "Energy": 2}
    values = article.get_topic_analyses_insert_values(topic_id_map)

    assert values == [
        (99, 1, 0.2, 0.3, 0.1, 0.05),
        (99, 2, 0.4, 0.4, 0.1, 0.2),
    ]
