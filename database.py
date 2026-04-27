import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def connect_db():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("Al_Barakah_DB") # নিশ্চিত হোন শিটের নাম ঠিক আছে
        return sheet
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# এই ফাংশনটি এখন থেকে সব জায়গায় মেম্বার লিস্ট সাপ্লাই দিবে
@st.cache_data(ttl=5)
def get_members():
    db_conn = connect_db()
    if db_conn:
        try:
            worksheet = db_conn.worksheet("Members")
            data = worksheet.get_all_records()
            return data
        except:
            return []
    return []

def add_savings(data_row):
    db_conn = connect_db()
    if db_conn:
        try:
            worksheet = db_conn.worksheet("Savings")
            worksheet.append_row(data_row)
            return True
        except:
            return False
    return False

# মেম্বার লিস্ট ভেরিয়েবল
members_list = get_members()
