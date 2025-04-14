import streamlit as st


col1, col2 = st.columns([1, 5])

with col1:
    st.image("logo.png", width=150)


st.image("logo.png")
st.title("Tilt")

st.write("""
    Welcome to the Tilts media bias database dashboard.
    This dashboard allows users to examine bias between news organisations
""")

st.subheader("Key metrics for each day Page:")
st.write("""
    This page includes key metrics on articles and topics for each paper for the day
""")

st.subheader("Subjectivity Page:")
st.write("""
    This page includes metrics on subjectivity like top 5 most postiive and negative articles for each paper
""")


st.subheader("Overall articles Page:")
st.write("""
    This page includes metrics over a longer period for each paper as well as the share of positive and negative articles each paper has
""")

st.subheader("Metrics explanation:")
st.write("""
    sentimenet: 4 metrics are avalaible for sentiment positive negative neutural and compound compound is .....
    
    subjectivity: how emotive the lanugage of the paper is. "hot chocolate is a popular beverage" vs "hot chocolate is tolerated by the masses"
         
    polarity: is another way of assessing sentiment. It doesnt measure how severe a sentiment is. for example 
         "I dont like that" would register the same as "I HATE THAT" where as the compound value for sentiment would take 
         that into account


""")
