import os
import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# df = pd.DataFrame({
#     'first column': [1, 2, 3, 4],
#     'second column': [10, 20, 30, 40]
# })
load_dotenv()
conn = psycopg2.connect(
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"]
)
df = pd.read_sql("SELECT * FROM article", conn)

st.write(df)
