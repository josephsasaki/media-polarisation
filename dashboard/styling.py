'''
    Script containing styling features for each page. The styling contributes towards the
    branch image.
'''

import streamlit as st


def title_image() -> None:
    '''Display the title image.'''
    st.image('static/title.png', use_container_width=True)


def top_bar() -> None:
    '''Display the top-bar for each page.'''
    st.image('static/top_bar.png', use_container_width=True)


def bottom_bar() -> None:
    '''Display the bottom-bar for each page.'''
    st.image('static/bottom_bar.png', use_container_width=True)
