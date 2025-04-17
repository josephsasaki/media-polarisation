'''
    The main entry point for the dashboard.
'''

import streamlit as st


if __name__ == "__main__":
    pg = st.navigation([
        st.Page("welcome.py", title="Welcome",
                icon=":material/home:"),
        st.Page("page1.py", title="Topic Polarisation",
                icon=":material/compare_arrows:"),
        st.Page("page2.py", title="Article Extremes",
                icon=":material/e911_emergency:"),
        st.Page("page3.py", title="News Outlet Sentiment",
                icon=":material/newspaper:"),
        st.Page("page4.py", title="Topic Sentiment",
                icon=":material/tag:"),
    ])
    pg.run()
