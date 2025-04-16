'''
    Module containing code for a page. This page contains graphs...
'''

from datetime import datetime
from newspaper import Article
import streamlit as st
import pandas as pd

from database_manager import query_data
from styling import top_bar, bottom_bar


METRIC_COLUMN_MAP = {
    "Positivity": "article_positive_sentiment",
    "Negativity": "article_negative_sentiment",
    "Subjectivity": "article_subjectivity",
    "Polarity": "article_polarity",
}


def info() -> None:
    '''Print the page information.'''
    st.header("Article Extremes", )
    st.write('''
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam rutrum nulla in tempor vulputate. 
            Nam a porta orci, non tempor enim. Ut finibus aliquam orci, eu faucibus nunc ultrices at. 
            Suspendisse porttitor ligula vitae auctor porta. Fusce non ante aliquam, convallis mauris nec, 
            rutrum ante. Nullam vel arcu leo. Suspendisse pharetra, neque in viverra lacinia, est ex cursus 
            leo, nec tempor nulla nunc sit amet magna. Cras fermentum maximus orci, a tempus dui interdum ut.
        '''
             )


def get_widget_inputs() -> tuple[str]:
    '''Get the specified day and metric.'''
    left_column, right_column, _, _ = st.columns(4)
    with left_column:
        day = st.date_input("Date", datetime.now().date(),
                            max_value=datetime.now().date())
    with right_column:
        metric = st.selectbox(
            "Metric",
            METRIC_COLUMN_MAP.keys(),
        )
    return {'day': day, 'metric': metric}


def retrieve_data(inputs: dict) -> pd.DataFrame:
    '''Retrieve the required data from the database.'''
    # Convert the chosen metric into a column name
    metric_column = METRIC_COLUMN_MAP[inputs['metric']]
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


def transform(df: pd.DataFrame, inputs: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    '''Transform the dataframe.'''
    metric_column = METRIC_COLUMN_MAP[inputs['metric']]
    guardian_df = df[df['news_outlet_name'] == 'The Guardian'].sort_values(
        by=metric_column, ascending=False).head(3)
    express_df = df[df['news_outlet_name'] == 'Daily Express'].sort_values(
        by=metric_column, ascending=False).head(3)
    return guardian_df, express_df


def write(guardian_df: pd.DataFrame, express_df: pd.DataFrame, inputs: dict) -> None:
    '''Write the streamlit page elements (except widgets).'''
    metric_column = METRIC_COLUMN_MAP[inputs['metric']]
    _, guardian_column, express_column = st.columns(
        [1, 8, 8],)
    with guardian_column:
        st.subheader("The Guardian")
    with express_column:
        st.subheader("Daily Express")
    st.markdown("<br>", unsafe_allow_html=True)

    for rank in range(1, 4):
        rank_col, left_column, right_column = st.columns(
            [1, 8, 8], vertical_alignment='center')
        with rank_col:
            st.subheader(str(rank))
        with left_column:
            row = guardian_df.iloc[rank-1]
            show_article_block(
                get_main_image(row["article_url"]),
                row["article_headline"],
                row["article_url"],
                row[metric_column]
            )
        with right_column:
            row = express_df.iloc[rank-1]
            show_article_block(
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
        <div style="display: flex; flex-direction: row; align-items: center;">
            <div style="height: 10px; width: {normal_value*100}%; background-color: #3d85c6; border-radius: 3px; margin-right: 0.2em;"></div>
            <span style="color: #3d85c6; font-size: smaller;">{normal_value:.1%}</span>
        </div>
    '''


def show_article_block(image_url: str, headline: str, article_url: str, metric_value: float) -> None:
    '''Write to the dashboard a single article block.'''
    st.markdown(article_bar_html(
        metric_value), unsafe_allow_html=True)
    image, info = st.columns([0.4, 0.6])
    with image:
        st.image(image_url)
    with info:
        st.write(headline)
        st.write(f"[Article link]({article_url})")
    st.markdown("<br>", unsafe_allow_html=True)


def show() -> None:
    '''From this method, the entire streamlit page is produced.'''
    top_bar()
    info()
    inputs = get_widget_inputs()
    df = retrieve_data(inputs)
    guardian_df, express_df = transform(df, inputs)
    write(guardian_df, express_df, inputs)
    bottom_bar()


if __name__ == "__main__":
    show()
