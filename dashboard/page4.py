import os
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

load_dotenv()


def connect_to_database() -> psycopg2.extensions.connection:
    """Connects to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        raise


@st.cache_data()
def get_data_from_database(query: str) -> pd.DataFrame:
    """Fetches data from the PostgreSQL database and returns it as a pandas DataFrame"""
    conn = connect_to_database()
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error occurred while fetching data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def average_compound_topic_line_graph(selected_topic: str) -> None:
    '''Line graph for average compound by day per paper'''

    query = """SELECT article_topic_compound_sentiment, news_outlet_name, article_published_date,topic_name FROM article
    JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
    JOIN article_topic on article_topic.article_id = article.article_id
    JOIN topic on topic.topic_id = article_topic.topic_id
    """
    data = get_data_from_database(query)
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

    query = """SELECT article_topic_positive_sentiment, news_outlet_name, article_published_date,topic_name FROM article
    JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
    JOIN article_topic on article_topic.article_id = article.article_id
    JOIN topic on topic.topic_id = article_topic.topic_id
    """
    data = get_data_from_database(query)
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

    query = """SELECT article_topic_negative_sentiment, news_outlet_name, article_published_date,topic_name FROM article
    JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
    JOIN article_topic on article_topic.article_id = article.article_id
    JOIN topic on topic.topic_id = article_topic.topic_id
    """
    data = get_data_from_database(query)
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


def get_all_topics() -> list:
    query = "SELECT DISTINCT topic_name FROM topic"
    data = get_data_from_database(query)
    unique_topics = sorted(data['topic_name'].dropna().unique().tolist())
    topic_multi = st.selectbox('Select Topic', unique_topics)
    return topic_multi


if __name__ == "__main__":
    all_topics = get_all_topics()
    average_compound_topic_line_graph(all_topics)
    average_positive_topic_line_graph(all_topics)
    average_negative_topic_line_graph(all_topics)
