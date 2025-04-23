'''
    Module containing code for a page. This page contains graphs...
'''

import plotly.graph_objects as go
import streamlit as st
import pandas as pd


from database_manager import query_data
from styling import top_bar, bottom_bar


def info() -> None:
    '''Print the page information.'''
    st.header("Topic Polarisation", )
    st.write('''
        This page explores how The Guardian and The Express cover news topics differently. 
        The first chart highlights the top five topics where the two publications disagree the most, 
        showcasing areas of strong editorial contrast. 
        The second chart reveals the top five topics where they show the most agreement, providing insight into shared narratives across divergent media outlets.
        '''
             )


def retrieve_data() -> pd.DataFrame:
    '''Method for querying data using the query_data method.'''
    query = """
        SELECT article_topic_compound_sentiment, news_outlet_name, article_published_date, topic_name 
        FROM article
        JOIN news_outlet ON news_outlet.news_outlet_id = article.news_outlet_id
        JOIN article_topic ON article_topic.article_id = article.article_id
        JOIN topic ON topic.topic_id = article_topic.topic_id
    """
    return query_data(query)


def get_widget_inputs(df: pd.DataFrame) -> tuple:
    '''Get the date range.'''
    min_date = df['article_published_date'].min()
    max_date = df['article_published_date'].max()
    col1, _ = st.columns([1, 2])
    with col1:
        date_range = st.date_input(
            "Select date range:",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
    if len(date_range) == 2:
        start_date, end_date = date_range
        return {"start_date": start_date, "end_date": end_date}
    return None


def transform_data(df: pd.DataFrame, inputs: dict) -> pd.DataFrame:
    '''Each page will require different transformations of the data. This
    method is for transforming the data.'''
    df = df[(df['article_published_date'] >= pd.to_datetime(inputs['start_date'])) &
            (df['article_published_date'] <= pd.to_datetime(inputs['end_date']))]
    grouped = df.groupby(['topic_name', 'news_outlet_name'])[
        'article_topic_compound_sentiment'].mean().reset_index()
    paper1_scores = grouped[grouped['news_outlet_name'] == 'The Guardian']
    paper2_scores = grouped[grouped['news_outlet_name'] == 'Daily Express']
    merged = pd.merge(
        paper1_scores[['topic_name', 'article_topic_compound_sentiment']],
        paper2_scores[['topic_name', 'article_topic_compound_sentiment']],
        on='topic_name',
        suffixes=('_The_Guardian', '_Daily_Express')
    )
    merged['difference'] = merged['article_topic_compound_sentiment_The_Guardian'] - \
        merged['article_topic_compound_sentiment_Daily_Express']
    return merged


def make_agreeable_chart(df: pd.DataFrame) -> None:
    '''Chart showing which topics the papers agree on the most'''
    closest = df['difference'].abs().nsmallest(5)
    closest_topics = df.loc[closest.index]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=closest_topics['topic_name'],
        x=closest_topics['article_topic_compound_sentiment_The_Guardian'],
        name='The Guardian Sentiment',
        orientation='h',
        marker_color='royalblue'
    ))
    fig.add_trace(go.Bar(
        y=closest_topics['topic_name'],
        x=closest_topics['article_topic_compound_sentiment_Daily_Express'],
        name='The Express Sentiment',
        orientation='h',
        marker_color='firebrick'
    ))
    fig.update_layout(
        title='Most Agreed Topic Sentiments',
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


def make_disagreeable_chart(df: pd.DataFrame) -> None:
    '''Chart showing which topics the papers disagree on the most'''
    closest = df['difference'].abs().nlargest(5)
    closest_topics = df.loc[closest.index]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=closest_topics['topic_name'],
        x=closest_topics['article_topic_compound_sentiment_The_Guardian'],
        name='The Guardian Sentiment',
        orientation='h',
        marker_color='royalblue'
    ))
    fig.add_trace(go.Bar(
        y=closest_topics['topic_name'],
        x=closest_topics['article_topic_compound_sentiment_Daily_Express'],
        name='The Express Sentiment',
        orientation='h',
        marker_color='firebrick'
    ))
    fig.update_layout(
        title='Most Disagreed Topic Sentiments',
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


def show() -> None:
    '''From this method, the entire streamlit page is produced.'''
    top_bar()
    info()
    df = retrieve_data()
    inputs = get_widget_inputs(df)
    if inputs is not None:
        df = transform_data(df, inputs)
        make_agreeable_chart(df)
        make_disagreeable_chart(df)
        bottom_bar()


if __name__ == "__main__":
    show()
