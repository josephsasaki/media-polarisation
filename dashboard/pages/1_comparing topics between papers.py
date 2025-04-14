import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pandas as pd

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


def most_agreeable_topics(df):
    '''Chart showing which topics the papers agree on the most'''

    closest = df['difference'].abs().nsmallest(5)
    closest_topics = df.loc[closest.index]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=closest_topics['topic_name'],
        x=closest_topics['article_topic_compound_sentiment_The_Guardian'],
        name=f'The Guardian Sentiment',
        orientation='h',
        marker_color='royalblue'
    ))

    fig.add_trace(go.Bar(
        y=closest_topics['topic_name'],
        x=closest_topics['article_topic_compound_sentiment_Daily_Express'],
        name=f'The Express Sentiment',
        orientation='h',
        marker_color='firebrick'
    ))

    fig.update_layout(
        title='Sentiment of Closest 5 Topics for Two Papers',
        xaxis_title='Sentiment Score (-1 to +1)',
        yaxis_title='Topic',
        xaxis=dict(range=[-1, 1], zeroline=True,
                   zerolinecolor='black', zerolinewidth=2),
        barmode='group',
        template='plotly_white',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True,
                    key="most_agreeable_topics_chart")


def most_disagreeable_topics(df):
    '''Chart showing which topics the papers disagree on the most'''

    closest = df['difference'].abs().nlargest(5)
    closest_topics = df.loc[closest.index]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=closest_topics['topic_name'],
        x=closest_topics['article_topic_compound_sentiment_The_Guardian'],
        name=f'The Guardian Sentiment',
        orientation='h',
        marker_color='royalblue'
    ))

    fig.add_trace(go.Bar(
        y=closest_topics['topic_name'],
        x=closest_topics['article_topic_compound_sentiment_Daily_Express'],
        name=f'The Express Sentiment',
        orientation='h',
        marker_color='firebrick'
    ))

    fig.update_layout(
        title='Sentiment of Closest 5 Topics for Two Papers',
        xaxis_title='Sentiment Score (-1 to +1)',
        yaxis_title='Topic',
        xaxis=dict(range=[-1, 1], zeroline=True,
                   zerolinecolor='black', zerolinewidth=2),
        barmode='group',
        template='plotly_white',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True,
                    key="most_disagreeable_topics_chart")


def filtered_date() -> pd.DataFrame:
    '''enables user to select the dates to view it from'''
    query = """SELECT article_topic_compound_sentiment, news_outlet_name, article_published_date, topic_name 
               FROM article
               JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
               JOIN article_topic ON article_topic.article_id = article.article_id
               JOIN topic ON topic.topic_id = article_topic.topic_id"""

    data = get_data_from_database(query)
    min_date = data['article_published_date'].min()
    max_date = data['article_published_date'].max()

    date_range = st.date_input(
        "Select date range:",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    start_date, end_date = date_range

    data = data[(data['article_published_date'] >= pd.to_datetime(start_date)) &
                (data['article_published_date'] <= pd.to_datetime(end_date))]

    return data


def find_difference(df: pd.DataFrame) -> pd.DataFrame:
    '''outputs a df with the difference between sentiment on a topic'''
    grouped = df.groupby(['topic_name', 'news_outlet_name'])[
        'article_topic_compound_sentiment'].mean().reset_index()

    paper1_scores = grouped[grouped['news_outlet_name'] == 'The Guardian']
    paper2_scores = grouped[grouped['news_outlet_name'] == 'Daily Express']

    merged = pd.merge(paper1_scores[['topic_name', 'article_topic_compound_sentiment']],
                      paper2_scores[['topic_name',
                                     'article_topic_compound_sentiment']],
                      on='topic_name',
                      suffixes=('_The_Guardian', '_Daily_Express'))

    merged['difference'] = merged['article_topic_compound_sentiment_The_Guardian'] - \
        merged['article_topic_compound_sentiment_Daily_Express']
    return merged


if __name__ == "__main__":

    df = filtered_date()
    diff_df = find_difference(df)
    most_agreeable_topics(diff_df)
    most_disagreeable_topics(diff_df)
