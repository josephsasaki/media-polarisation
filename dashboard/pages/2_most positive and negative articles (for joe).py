import os
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime, date

load_dotenv()

IMG_URL = "https://i.guim.co.uk/img/media/4db6b79d0a58121aa4d33520e7bdb06db3a62791/0_0_4724_2835/master/4724.jpg?width=460&quality=85&auto=format&fit=max&s=b36287f1daddc45cc2acd9e1b136d18b"


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
def get_data_from_database(query: str, params: tuple) -> pd.DataFrame:
    """Fetches data from the PostgreSQL database and returns it as a pandas DataFrame"""
    conn = connect_to_database()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Error occurred while fetching data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def get_widget_inputs() -> tuple[str]:
    '''Get user inputs from the widgets.'''
    left_column, right_column, _, _ = st.columns(4)
    with left_column:
        day = st.date_input("Date", datetime.now().date())
    with right_column:
        metric = st.selectbox(
            "Metric",
            ("Positivity", "Negativity", "Compound", "Subjectivity", "Polarity"),
        )
    return day, metric


def get_chart_data(day: date, metric: str) -> pd.DataFrame:
    metric_column = {
        "Positivity": "a.article_positive_sentiment",
        "Negativity": "a.article_negative_sentiment",
        "Compound": "a.article_compound_sentiment",
        "Subjectivity": "a.article_subjectivity",
        "Polarity": "a.article_polarity",
    }[metric]
    query = f'''
        SELECT
            news_outlet_name,
            a.article_headline,
            a.article_url,
            {metric_column}
        FROM article AS a
        JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
        WHERE a.article_published_date::date = %s
    '''
    return get_data_from_database(query, (day,))


def article_bar_html(normal_value: float) -> str:
    return f'''<div style="
            height: 10px; 
            width: {normal_value*100}%; 
            background-color: #e06767;
            border-radius: 3px;
        "></div>'''


def show_article_block(rank: int, image_url: str, headline: str, article_url: str, metric_value: float) -> None:
    '''Write to the dashboard a single article block.'''

    st.markdown(article_bar_html(metric_value), unsafe_allow_html=True)

    rank_col, image, info = st.columns(
        [0.1, 0.3, 0.6], vertical_alignment='center')
    with rank_col:
        st.write(str(rank))
    with image:
        st.image(image_url)
    with info:
        st.write(headline)
        st.write("[Article link](%s)" % article_url)

    st.markdown("<br><br>", unsafe_allow_html=True)


def show_chart():
    left_column, right_column = st.columns(2)
    with left_column:
        st.header("The Guardian")
        st.markdown("<br>", unsafe_allow_html=True)
        show_article_block(
            1,
            "https://i.guim.co.uk/img/media/fd0cafe542a657ce939f4f43e37d753ea24e37ee/0_704_3648_2189/master/3648.jpg?width=140&quality=85&auto=format&fit=max&s=69bc48bf2e41ad0d4c66c8a9255119e3",
            "Some Headline: Something Has Happened",
            "https://www.theguardian.com/uk",
            0.9,
        )
        show_article_block(
            2,
            "https://i.guim.co.uk/img/media/afffdee907a94e4c44c7ce21f14dc0d79712c19a/0_116_3460_2075/master/3460.jpg?width=140&quality=85&auto=format&fit=max&s=6d92b3757ea606b1295affb9ad4722e1",
            "Some Headline: Something Has Happened",
            "https://www.theguardian.com/uk",
            0.7,
        )
        show_article_block(
            3,
            "https://i.guim.co.uk/img/media/4db6b79d0a58121aa4d33520e7bdb06db3a62791/0_0_4724_2835/master/4724.jpg?width=140&quality=85&auto=format&fit=max&s=26ec936ab153d5c31003e11c4232f859",
            "Some Headline: Something Has Happened",
            "https://www.theguardian.com/uk",
            0.4,
        )
    with right_column:
        st.header("Daily Express")
        st.markdown("<br>", unsafe_allow_html=True)
        show_article_block(
            1,
            "https://i.guim.co.uk/img/media/a8289741785420bc2f68d0c3aa491d9ace09f8e0/0_0_7728_4637/master/7728.jpg?width=140&quality=85&auto=format&fit=max&s=649daf351078f037c32e50f3b37957bb",
            "Some Headline: Something Has Happened",
            "https://www.theguardian.com/uk",
            0.8,
        )
        show_article_block(
            2,
            "https://i.guim.co.uk/img/media/dad848f01725d976fe6449ff903ea195e3bb7eaf/0_0_6000_3600/master/6000.jpg?width=140&quality=85&auto=format&fit=max&s=67c2272c8fb41c43927285d24cb3fc52",
            "Some Headline: Something Has Happened",
            "https://www.theguardian.com/uk",
            0.6,
        )
        show_article_block(
            3,
            "https://i.guim.co.uk/img/media/85330df5cf76e7e6e9e19a9cbcc64240fc791c71/0_116_3500_2101/master/3500.jpg?width=140&quality=85&auto=format&fit=max&s=f88fd3ac3c34cdc9672aa2ce65186ea9",
            "Some Headline: Something Has Happened",
            "https://www.theguardian.com/uk",
            0.5,
        )


if __name__ == "__main__":
    day, metric = get_widget_inputs()
    df = get_chart_data(day, metric)
    show_chart()
