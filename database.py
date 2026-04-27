import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- Google Sheets Connection ---
def connect_db():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        # আপনার শিটের নাম হুবহু মিল থাকতে হবে
        sheet = client.open("Al_Barakah_DB") 
        return sheet
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# --- মেম্বার ডাটা লোড করা ---
@st.cache_data(ttl=5)
def get_live_data():
    db_conn = connect_db()
    if db_conn:
        try:
            worksheet = db_conn.worksheet("Members")
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            df = df.fillna("")
            if 'ID' in df.columns:
                df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
            return df.to_dict('records')
        except:
            return []
    return []

# --- সেভিংস সেভ করা ---
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

# মেম্বার লিস্ট ভেরিয়েবল (main.py এর জন্য)
members_list = get_live_data()
