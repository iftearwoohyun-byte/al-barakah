import streamlit as st
import pandas as pd
import requests
from io import StringIO

# আপনার দেওয়া পাবলিক CSV লিঙ্ক
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQVKDrHpiR1S2Qbh6c7FeM3HjiPILQSwH2YLb-ueDWVMtOznyjFqVHOiDWyAP2gQ/pub?output=csv"

@st.cache_data(ttl=5) # প্রতি ৫ সেকেন্ড পর পর নতুন ডাটা চেক করবে
def get_live_data():
    try:
        # সরাসরি লিঙ্ক থেকে ডাটা রিড করা
        response = requests.get(CSV_URL)
        if response.status_code == 200:
            # ইউনিকোড ফিক্স করে ডাটা পড়া (বাংলা থাকলেও সমস্যা হবে না)
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            # ডাটা ক্লিন করা: যদি কোনো কলামে ডাটা না থাকে তবে ফাকা দেখাবে
            df = df.fillna("")
            
            # নিশ্চিত করা যে আইডি কলামটি সংখ্যা হিসেবে আছে
            if 'ID' in df.columns:
                df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
            
            return df.to_dict('records')
        else:
            return []
    except Exception as e:
        st.error(f"ডাটা কানেকশনে সমস্যা: {e}")
        return []

# ডাটা লিস্ট কল করা
members_list = get_live_data()
