'''
    Module containing code for a page. This page contains graphs...
'''

import streamlit as st
import plotly.express as px

from database_manager import query_data
from styling import top_bar, bottom_bar


def info() -> None:
    '''Print the page information.'''
    st.header("News Outlet Sentiment", )
    st.write('''
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam rutrum nulla in tempor vulputate. 
            Nam a porta orci, non tempor enim. Ut finibus aliquam orci, eu faucibus nunc ultrices at. 
            Suspendisse porttitor ligula vitae auctor porta. Fusce non ante aliquam, convallis mauris nec, 
            rutrum ante. Nullam vel arcu leo. Suspendisse pharetra, neque in viverra lacinia, est ex cursus 
            leo, nec tempor nulla nunc sit amet magna. Cras fermentum maximus orci, a tempus dui interdum ut.
        '''
             )


def average_subjectivity_line_graph() -> None:
    '''Line graph for average subjectivity by day per paper'''
    query = """SELECT article_subjectivity, news_outlet_name, article_published_date FROM article
    JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
    """
    data = query_data(query)
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
        title='News Outlet Subjectivity',
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
    data = query_data(query)
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
        title='News Outlet Polarity',
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
    query = """
        SELECT 
            article_compound_sentiment, 
            news_outlet_name, 
            article_published_date 
        FROM article
        JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
    """
    data = query_data(query)
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
        title='News Outlet Compound Sentiment',
        markers=True,
        color_discrete_map={"The Guardian": "red", "Daily Express": "blue"}
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Average Compound Sentiment',
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    st.plotly_chart(fig)


def show() -> None:
    '''Show the complete page.'''
    top_bar()
    info()
    average_subjectivity_line_graph()
    average_polarity_line_graph()
    average_compound_line_graph()
    bottom_bar()


if __name__ == "__main__":
    show()
