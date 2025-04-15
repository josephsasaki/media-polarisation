from newspaper import Article
import os
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from datetime import datetime, date

load_dotenv()

IMG_URL = "https://i.guim.co.uk/img/media/4db6b79d0a58121aa4d33520e7bdb06db3a62791/0_0_4724_2835/master/4724.jpg?width=460&quality=85&auto=format&fit=max&s=b36287f1daddc45cc2acd9e1b136d18b"


def get_main_image(article_url):
    article = Article(article_url)
    article.download()
    article.parse()
    return article.top_image


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


def show_chart(df: pd.DataFrame, metric: str):
    left_column, right_column = st.columns(2)

    metric_column = {
        "Positivity": "article_positive_sentiment",
        "Negativity": "article_negative_sentiment",
        "Compound": "article_compound_sentiment",
        "Subjectivity": "article_subjectivity",
        "Polarity": "article_polarity",
    }[metric]

    guardian_df = df[df['news_outlet_name'] == 'The Guardian'].sort_values(
        by=metric_column, ascending=False).head(3)
    express_df = df[df['news_outlet_name'] == 'Daily Express'].sort_values(
        by=metric_column, ascending=False).head(3)

    with left_column:
        st.header("The Guardian")
        st.markdown("<br>", unsafe_allow_html=True)
        for rank, (_, row) in enumerate(guardian_df.iterrows(), start=1):
            show_article_block(
                rank,
                get_main_image(row["article_url"]),
                row["article_headline"],
                row["article_url"],
                row[metric_column]
            )

    with right_column:
        st.header("Daily Express")
        st.markdown("<br>", unsafe_allow_html=True)
        for rank, (_, row) in enumerate(express_df.iterrows(), start=1):
            show_article_block(
                rank,
                get_main_image(row["article_url"]),
                row["article_headline"],
                row["article_url"],
                row[metric_column]
            )


if __name__ == "__main__":
    day, metric = get_widget_inputs()
    df = get_chart_data(day, metric)
    if df.empty:
        st.warning("No articles found for the selected date.")
    else:
        show_chart(df, metric)
