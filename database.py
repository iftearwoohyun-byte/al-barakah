import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- ১. গুগল শিট কানেকশন (গোপন Secrets ব্যবহার করে) ---
def connect_db():
    try:
        # Streamlit Secrets থেকে ক্রেডেনশিয়াল নেওয়া
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # আপনার তৈরি করা গুগল শিটের নাম
        sheet = client.open("Al_Barakah_DB")
        return sheet
    except Exception as e:
        st.error(f"ডাটাবেজ কানেকশনে সমস্যা: {e}")
        return None

# --- ২. মেম্বার লিস্ট পড়া (আপনার আগের লিস্টের মতো কাজ করবে) ---
@st.cache_data(ttl=5) # ৫ সেকেন্ড পর পর আপডেট হবে
def get_live_data():
    db = connect_db()
    if db:
        try:
            worksheet = db.worksheet("Members")
            data = worksheet.get_all_records()
            
            # ডাটা ক্লিন করা (আপনার আগের কোডের মতো)
            df = pd.DataFrame(data)
            df = df.fillna("")
            if 'ID' in df.columns:
                df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
            
            return df.to_dict('records')
        except Exception as e:
            st.error(f"মেম্বার ডাটা পড়তে সমস্যা: {e}")
            return []
    return []

# --- ৩. সেভিংস ডাটা সেভ করার ফাংশন ---
def add_savings(data_row):
    """গুগল শিটের Savings ট্যাবে ডাটা যোগ করবে"""
    db = connect_db()
    if db:
        try:
            worksheet = db.worksheet("Savings")
            worksheet.append_row(data_row)
            return True
        except Exception as e:
            st.error(f"সেভিংস সেভ করতে সমস্যা: {e}")
            return False
    return False

# --- ৪. ব্যাংক ডাটা সেভ করার ফাংশন ---
def add_bank_record(data_row):
    """গুগল শিটের Bank ট্যাবে ডাটা যোগ করবে"""
    db = connect_db()
    if db:
        try:
            worksheet = db.worksheet("Bank")
            worksheet.append_row(data_row)
            return True
        except Exception as e:
            st.error(f"ব্যাংক ডাটা সেভ করতে সমস্যা: {e}")
            return False
    return False

# আপনার অ্যাপের অন্যান্য পেইজে যাতে মেম্বার লিস্ট পায় তার জন্য:
members_list = get_live_data()
