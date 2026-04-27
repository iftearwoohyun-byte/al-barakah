import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime
import database as db

# --- অটো ডাটা রিড করার লজিক ---
def fetch_fdr_details(url):
    try:
        # ব্যাংক ওয়েবসাইট থেকে ডাটা পড়ার চেষ্টা
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ট্রাস্ট ব্যাংকের ই-সার্ভিস পেজ অনুযায়ী ডাটা খোঁজা
            # নোট: ব্যাংকের পেজ স্ট্রাকচার পরিবর্তন হলে এই লজিক আপডেট করতে হবে
            tables = soup.find_all('table')
            extracted_data = {"amount": 0.0, "mature_date": datetime.now()}
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    text = row.get_text().lower()
                    if 'amount' in text:
                        # সংখ্যা খুঁজে বের করা
                        val = ''.join(filter(str.isdigit, row.get_text()))
                        extracted_data["amount"] = float(val) if val else 0.0
                    if 'maturity' in text or 'date' in text:
                        # তারিখ খুঁজে বের করা (সাধারণ ফরম্যাট অনুযায়ী)
                        # এটি একটি সিম্পল লজিক, অনেক সময় ফরম্যাট ভিন্ন হতে পারে
                        pass 
            return extracted_data
    except:
        return None
    return None

# --- FDR ফর্ম ডিজাইন (অপরিবর্তিত ডিজাইন) ---
@st.dialog("➕ ADD NEW FDR")
def open_add_fdr_form():
    st.write("### NEW FDR ENTRY")
    
    # প্রথমে লিঙ্ক ইনপুট
    fdr_url = st.text_input("Paste FDR Bank Link (URL)")
    
    # অটো-রিড বাটন
    if st.button("🔍 AUTO FILL FROM LINK", use_container_width=True):
        if fdr_url:
            with st.spinner("Fetching data from bank..."):
                details = fetch_fdr_details(fdr_url)
                if details:
                    st.session_state['auto_amt'] = details['amount']
                    st.success("Data fetched successfully!")
                else:
                    st.warning("Could not auto-read. Please enter details manually.")
        else:
            st.error("Please paste a link first!")

    # ইনপুট ফিল্ডগুলো (অটো-ফিল ভ্যালুসহ)
    amount = st.number_input("Amount (Taka)", 
                             value=st.session_state.get('auto_amt', 0.0), 
                             min_value=0.0, step=500.0)
    
    o_date = st.date_input("Opening Date", datetime.now())
    m_date = st.date_input("Maturity Date", datetime.now())
    status = st.selectbox("Status", ["Active", "Matured"])
    
    if st.button("SAVE RECORD", type="primary", use_container_width=True):
        conn = db.connect_db()
        if conn:
            try:
                worksheet = conn.worksheet("FDR_Data")
                new_id = len(worksheet.get_all_values())
                worksheet.append_row([
                    new_id, 
                    o_date.strftime('%m/%d/%y'), 
                    m_date.strftime('%m/%d/%y'), 
                    amount, 
                    status, 
                    fdr_url
                ])
                st.success("FDR Saved Successfully!")
                # সেশন ডাটা ক্লিয়ার করা
                if 'auto_amt' in st.session_state: del st.session_state['auto_amt']
                st.rerun()
            except:
                st.error("গুগল শিটে 'FDR_Data' ট্যাবটি আছে কি না নিশ্চিত করুন!")
