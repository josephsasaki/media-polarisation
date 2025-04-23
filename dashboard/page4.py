'''
    Module containing code for a page. This page contains graphs...
'''

import streamlit as st
import plotly.express as px

from database_manager import query_data
from styling import top_bar, bottom_bar


def info() -> None:
    '''Print the page information.'''
    st.header("Topic Sentiment", )
    st.write('''
            This page presents a deep dive into how The Guardian and The Daily Express express sentiment on 
            specific topics. Use the dropdown menu above to choose a topic. Three line charts below show 
            how sentiment evolves over time for that topic: positive sentiment, negative sentiment, and 
            compound sentiment. Each graph includes a line for each publication, allowing direct comparison 
            of tone and framing across media sources.
        '''
             )


def get_all_topics() -> list[str]:
    '''Get all the topics.'''
    query = "SELECT DISTINCT topic_name FROM topic"
    data = query_data(query)
    unique_topics = sorted(data['topic_name'].dropna().unique().tolist())
    return unique_topics


def get_widget_inputs(all_topics: list[str]) -> str:
    '''Get the specified day and metric.'''
    left_column, _, = st.columns([1, 2])
    with left_column:
        trump_index = all_topics.index('Donald Trump')
        selected_topic = st.selectbox(
            'Select Topic', all_topics, index=trump_index)
    return selected_topic


def average_compound_topic_line_graph(selected_topic: str) -> None:
    '''Line graph for average compound by day per paper'''
    query = """
        SELECT 
            article_topic_compound_sentiment, 
            news_outlet_name, 
            article_published_date,
            topic_name 
        FROM article
        JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
        JOIN article_topic on article_topic.article_id = article.article_id
        JOIN topic on topic.topic_id = article_topic.topic_id
    """
    data = query_data(query)
    data['article_published_day'] = data['article_published_date'].dt.floor(
        'd')
    data = data[data['topic_name'] == selected_topic]
    avg_subjectivity = data.groupby(
        ['article_published_day', 'news_outlet_name']
    )['article_topic_compound_sentiment'].mean().reset_index()
    fig = px.line(
        avg_subjectivity,
        x='article_published_day',
        y='article_topic_compound_sentiment',
        color='news_outlet_name',
        title='Topic Compound Sentiment',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"},
        labels={"news_outlet_name": "News Outlet"}
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Average Topic Compound Sentiment',
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    st.plotly_chart(fig)


def average_positive_topic_line_graph(selected_topic: str) -> None:
    '''Line graph for average compound by day per paper'''
    query = """
        SELECT 
            article_topic_positive_sentiment, 
            news_outlet_name, 
            article_published_date,
            topic_name 
        FROM article
        JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
        JOIN article_topic on article_topic.article_id = article.article_id
        JOIN topic on topic.topic_id = article_topic.topic_id
    """
    data = query_data(query)
    data['article_published_day'] = data['article_published_date'].dt.floor(
        'd')
    data = data[data['topic_name'] == selected_topic]

    avg_subjectivity = data.groupby(
        ['article_published_day', 'news_outlet_name']
    )['article_topic_positive_sentiment'].mean().reset_index()

    fig = px.line(
        avg_subjectivity,
        x='article_published_day',
        y='article_topic_positive_sentiment',
        color='news_outlet_name',
        title='Topic Positive Sentiment',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"},
        labels={"news_outlet_name": "News Outlet"}
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Average Topic Positive Sentiment',
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    st.plotly_chart(fig)


def average_negative_topic_line_graph(selected_topic: str) -> None:
    '''Line graph for average negative sentiment by day per paper'''

    query = """
        SELECT 
            article_topic_negative_sentiment, 
            news_outlet_name, 
            article_published_date,
            topic_name 
        FROM article
        JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
        JOIN article_topic on article_topic.article_id = article.article_id
        JOIN topic on topic.topic_id = article_topic.topic_id
    """
    data = query_data(query)
    data['article_published_day'] = data['article_published_date'].dt.floor(
        'd')
    data = data[data['topic_name'] == selected_topic]

    avg_subjectivity = data.groupby(
        ['article_published_day', 'news_outlet_name']
    )['article_topic_negative_sentiment'].mean().reset_index()

    fig = px.line(
        avg_subjectivity,
        x='article_published_day',
        y='article_topic_negative_sentiment',
        color='news_outlet_name',
        title='Topic Negative Sentiment',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"},
        labels={"news_outlet_name": "News Outlet"}
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Average Topic Negative Sentiment',
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    st.plotly_chart(fig)


def show() -> None:
    '''Show the complete page.'''
    top_bar()
    info()
    all_topics = get_all_topics()
    selected_topic = get_widget_inputs(all_topics)
    average_compound_topic_line_graph(selected_topic)
    average_positive_topic_line_graph(selected_topic)
    average_negative_topic_line_graph(selected_topic)
    bottom_bar()


if __name__ == "__main__":
    show()
