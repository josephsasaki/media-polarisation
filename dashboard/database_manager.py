'''
    The following script defines functions for accessing the database.
'''

import os
import psycopg2
import streamlit as st
import pandas as pd
from dotenv import load_dotenv


def create_connection() -> psycopg2.extensions.connection:
    '''Connects to the PostgreSQL database.'''
    load_dotenv()
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        raise


@st.cache_data()
def query_data(query: str, params: tuple = None) -> pd.DataFrame:
    '''Fetches data from the PostgreSQL database and returns it as a pandas DataFrame.'''
    conn = create_connection()
    try:
        return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.error(f"Error occurred while fetching data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
