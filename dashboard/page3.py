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


def average_subjectivity_line_graph() -> None:
    '''Line graph for average subjectivity by day per paper'''

    query = """SELECT article_subjectivity, news_outlet_name, article_published_date FROM article
    JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
    """
    data = get_data_from_database(query)
    data['article_published_day'] = data['article_published_date'].dt.floor(
        'd')

    avg_subjectivity = data.groupby(
        ['article_published_day', 'news_outlet_name']
    )['article_subjectivity'].mean().reset_index()

    fig = px.line(
        avg_subjectivity,
        x='article_published_day',
        y='article_subjectivity',
        color='news_outlet_name',
        title='Average Article Subjectivity Over Time by News Outlet',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"}
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Average Subjectivity',
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    st.plotly_chart(fig)


def average_polarity_line_graph() -> None:
    '''Line graph for average polarity by day per paper'''

    query = """SELECT article_polarity, news_outlet_name, article_published_date FROM article
    JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
    """
    data = get_data_from_database(query)
    data['article_published_day'] = data['article_published_date'].dt.floor(
        'd')

    avg_subjectivity = data.groupby(
        ['article_published_day', 'news_outlet_name']
    )['article_polarity'].mean().reset_index()

    fig = px.line(
        avg_subjectivity,
        x='article_published_day',
        y='article_polarity',
        color='news_outlet_name',
        title='Average Article Polarity Over Time by News Outlet',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"}
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Average Polarity',
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    st.plotly_chart(fig)


def average_compound_line_graph() -> None:
    '''Line graph for average compound by day per paper'''

    query = """SELECT article_compound_sentiment, news_outlet_name, article_published_date FROM article
    JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
    """
    data = get_data_from_database(query)
    data['article_published_day'] = data['article_published_date'].dt.floor(
        'd')

    avg_subjectivity = data.groupby(
        ['article_published_day', 'news_outlet_name']
    )['article_compound_sentiment'].mean().reset_index()

    fig = px.line(
        avg_subjectivity,
        x='article_published_day',
        y='article_compound_sentiment',
        color='news_outlet_name',
        title='Average Article Compound Sentiment Over Time by News Outlet',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"}
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Average Compound Sentiment',
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    st.plotly_chart(fig)


if __name__ == "__main__":
    average_polarity_line_graph()
    average_subjectivity_line_graph()
    average_compound_line_graph()
