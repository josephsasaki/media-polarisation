'''
    The main entry point for the dashboard.
'''

import streamlit as st


if __name__ == "__main__":
    pg = st.navigation([
        st.Page("welcome.py", title="Welcome", icon="🔥"),
        st.Page("page1.py", title="First page", icon="🔥"),
        st.Page("page2.py", title="Second page", icon="🔥"),
        st.Page("page3.py", title="Third page", icon="🔥"),
        st.Page("page4.py", title="Fourth page", icon="🔥"),
    ])
    pg.run()
