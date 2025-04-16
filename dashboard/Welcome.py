'''
    The welcome page.
'''

import streamlit as st
from styling import title_image, bottom_bar


def title_generator():
    title_image()

    st.write("""
        Welcome to the Tilts media bias database dashboard.
        This dashboard allows users to examine bias between news organisations
    """)


def page_breakdown():
    st.header("Page Description")
    st.subheader("Topic Polarisation")
    st.write("""
        This page explores how The Guardian and The Express cover news topics differently. The first chart highlights the top five topics where the two publications disagree the most, showcasing areas of strong editorial contrast. 
        The second chart reveals the top five topics where they show the most agreement, providing insight into shared narratives across divergent media outlets.
    """)
    st.subheader("Article Extremes")
    st.write("""
        This page lets you explore how The Guardian and The Daily Express report on the news. Use the dropdowns above to filter articles by date and ranking metric—such as positivity, negativity, polarity, or subjectivity. The top 3 articles from each publication will then be shown side by side for easy comparison.
    """)
    st.subheader("News Outlet Sentiment")
    st.write("""
        This page visualizes how the tone and writing style of The Guardian and The Daily Express have changed over time. Three graphs display trends in subjectivity, polarity, and negativity, with separate lines for each publication. 
        These charts offer a clear comparison of how each outlet’s language and framing evolve across the selected time period.
    """)
    st.subheader("Topic Sentiment")
    st.write("This page presents a deep dive into how The Guardian and The Daily Express express sentiment on specific topics. Use the dropdown menu above to choose a topic. Three line charts below show how sentiment evolves over time for that topic: positive sentiment, negative sentiment, and compound sentiment. Each graph includes a line for each publication, allowing direct comparison of tone and framing across media sources.")


def metrics_explainer():
    st.header("Metrics Explanation:")
    st.subheader("Sentiment")
    st.write("""
There are four sentiment scores: positive, negative, neutral, and compound. The compound score combines all of these into a single number from -1.0 (most negative) to 1.0 (most positive), with 0.0 being neutral. VADER doesn’t just detect sentiment—it also accounts for the intensity of the language. Stronger or more emotionally charged words (like “fantastic” or “horrible”) have a bigger impact than milder terms (like “good” or “bad”), making the compound score a reflection of both the direction and strength of sentiment.
    """)
    st.subheader("Subjectivity")
    st.write("Is a value provided by TextBlob that measures how subjective or opinion-based a piece of text is. The value ranges from 0.0 to 1.0, where 0.0 represents completely objective statements and 1.0 indicates highly subjective content. Objective text tends to present facts, while subjective text includes personal opinions, emotions, or judgments.")
    st.subheader("Polarity")
    st.write("Is a value from TextBlob that measures the emotional tone of a piece of text. It ranges from -1.0 to 1.0, where -1.0 represents a very negative sentiment, 0.0 is neutral, and 1.0 indicates a very positive sentiment. This score helps identify whether the language used in a sentence or article expresses negative, neutral, or positive emotion.")

    bottom_bar()


if __name__ == "__main__":
    title_generator()
    page_breakdown()
    metrics_explainer()
