'''
    Module containing code for a page. This page contains graphs...
'''

from datetime import datetime
from newspaper import Article
import streamlit as st
import pandas as pd

from database_manager import query_data
from styling import top_bar, bottom_bar


def get_widget_inputs() -> tuple[str]:
    '''Get the specified day and metric.'''
    left_column, right_column, _, _ = st.columns(4)
    with left_column:
        day = st.date_input("Date", datetime.now().date())
    with right_column:
        metric = st.selectbox(
            "Metric",
            ("Positivity", "Negativity", "Compound", "Subjectivity", "Polarity"),
        )
    return {'day': day, 'metric': metric}


def retrieve_data(inputs: dict) -> pd.DataFrame:
    '''Retrieve the required data from the database.'''
    # Convert the chosen metric into a column name
    metric_column = {
        "Positivity": "a.article_positive_sentiment",
        "Negativity": "a.article_negative_sentiment",
        "Compound": "a.article_compound_sentiment",
        "Subjectivity": "a.article_subjectivity",
        "Polarity": "a.article_polarity",
    }[inputs['metric']]
    # define the sql query with the chosen metric
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
    return query_data(query=query, params=(inputs['day'],))


def write(df: pd.DataFrame, inputs: dict) -> None:
    '''Write the streamlit page elements (except widgets).'''
    left_column, right_column = st.columns(2)
    metric_column = {
        "Positivity": "article_positive_sentiment",
        "Negativity": "article_negative_sentiment",
        "Compound": "article_compound_sentiment",
        "Subjectivity": "article_subjectivity",
        "Polarity": "article_polarity",
    }[inputs['metric']]
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


def get_main_image(article_url: str):
    '''Get the article image from the url.'''
    article = Article(article_url)
    article.download()
    article.parse()
    return article.top_image


def article_bar_html(normal_value: float) -> str:
    '''Create the article metric bar above the article.'''
    return f'''
        <div style="
        height: 10px; 
        width: {normal_value*100}%; 
        background-color: #e06767;
        border-radius: 3px;
        "></div>
    '''


def show_article_block(rank: int, image_url: str, headline: str, article_url: str, metric_value: float) -> None:
    '''Write to the dashboard a single article block.'''
    st.markdown(article_bar_html(
        metric_value), unsafe_allow_html=True)
    rank_col, image, info = st.columns(
        [0.1, 0.3, 0.6], vertical_alignment='center')
    with rank_col:
        st.write(str(rank))
    with image:
        st.image(image_url)
    with info:
        st.write(headline)
        st.write(f"[Article link]({article_url})")
    st.markdown("<br><br>", unsafe_allow_html=True)


def show() -> None:
    '''From this method, the entire streamlit page is produced.'''
    top_bar()
    inputs = get_widget_inputs()
    df = retrieve_data(inputs)
    write(df, inputs)
    bottom_bar()


if __name__ == "__main__":
    show()
