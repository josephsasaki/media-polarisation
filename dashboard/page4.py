'''
    Module containing code for a page. This page contains graphs...
'''

import streamlit as st
import plotly.express as px

from database_manager import query_data


def get_all_topics() -> list:
    '''Get all the topics.'''
    query = "SELECT DISTINCT topic_name FROM topic"
    data = query_data(query)
    unique_topics = sorted(data['topic_name'].dropna().unique().tolist())
    topic_multi = st.selectbox('Select Topic', unique_topics)
    return topic_multi


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
        title='Average Topic Compound Sentiment Over Time by News Outlet',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"}
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
        title='Average Topic Positive Sentiment Over Time by News Outlet',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"}
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
        title='Average Topic Negative Sentiment Over Time by News Outlet',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"}
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Average Topic Negative Sentiment',
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    st.plotly_chart(fig)


def show() -> None:
    '''Show the complete page.'''
    all_topics = get_all_topics()
    average_compound_topic_line_graph(all_topics)
    average_positive_topic_line_graph(all_topics)
    average_negative_topic_line_graph(all_topics)


if __name__ == "__main__":
    show()
