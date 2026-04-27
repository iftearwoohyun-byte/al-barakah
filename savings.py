import streamlit as st
import pandas as pd
import database as db  # আমরা যে নতুন database.py বানিয়েছি সেটা
from datetime import datetime

# --- ১. ডাটা ফাংশন (এখন Google Sheets থেকে আসবে) ---
def load_savings_data():
    try:
        sheet = db.connect_db()
        worksheet = sheet.worksheet("Savings")
        return pd.DataFrame(worksheet.get_all_records())
    except:
        return pd.DataFrame()

# --- ২. কিস্তি জমার পপ-আপ (Google Sheets Sync সহ) ---
@st.dialog("Collect Savings")
def add_deposit():
    st.markdown("<h3 style='color:#1A365D;'>নতুন সঞ্চয় জমা করুন</h3>", unsafe_allow_html=True)
    
    # মেম্বার লিস্ট এখন গুগল শিট থেকে আসবে
    members_data = db.get_members() 
    
    if not members_data:
        st.error("মেম্বার লিস্ট খালি! গুগল শিটের 'Members' ট্যাবে মেম্বার যোগ করুন।")
        return

    names = [f"{m['Name']} (ID: {m['ID']})" for m in members_data]
    selected_member = st.selectbox("মেম্বার সিলেক্ট করুন", names)
    
    # মাস তৈরির লজিক (আপনার আগের লজিক)
    months = []
    for year in ["25", "26", "27"]:
        for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
            if year == "25" and m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]: continue
            if year == "27" and m in ["Nov", "Dec"]: continue
            months.append(f"{m}_{year}")
    
    selected_month = st.selectbox("মাস সিলেক্ট করুন", months)
    
    m_id = selected_member.split("(ID: ")[1].replace(")", "")
    member = next((m for m in members_data if str(m['ID']) == m_id), None)
    default_amt = int(member.get('Share', 1)) * 5000 if member else 0
    
    amount = st.text_input("জমার পরিমাণ", value=str(default_amt))

    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        # গুগল শিটে ডাটা পাঠানোর ফরম্যাট: [Date, ID, Name, Amount, Month, Year]
        today = datetime.now().strftime("%d/%m/%Y")
        month_only = selected_month.split("_")[0]
        year_only = "20" + selected_month.split("_")[1]
        
        row_to_add = [today, m_id, member['Name'], amount, month_only, year_only]
        
        if db.add_savings(row_to_add): # database.py এর ফাংশন কল
            st.success("গুগল শিটে সফলভাবে সেভ হয়েছে!")
            st.rerun()
        else:
            st.error("সেভ হতে সমস্যা হয়েছে।")

# --- ৩. মেইন শো ফাংশন (ডিজাইন আগের মতোই) ---
def show():
    st.markdown("""
        <style>
        .savings-header { background-color: #1A365D; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
        .header-text { color: white !important; font-size: 24px; font-weight: bold; }
        div.savings-btn-group button {
            height: 100px !important; font-size: 18px !important;
            background-color: #2D3748 !important; color: white !important; border-radius: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="savings-header"><h1 class="header-text">AL-BARAKAH SAVINGS LEDGER (GOOGLE CLOUD)</h1></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 4])
    with col1:
        if st.button("➕\nADD SAVINGS", key="add_sav_btn"):
            add_deposit()
    with col2:
        if st.button("🔄\nREFRESH DATA", key="sync_sav_btn"):
            st.rerun()

    # ৪. ডাটা টেবিল (গুগল শিট থেকে ডাটা নিয়ে এসে দেখানো)
    df_savings = load_savings_data()
    
    if not df_savings.empty:
        # এখানে আপনার আগের ক্যালকুলেশন লজিক থাকবে
        # গুগল শিট থেকে আসা ডাটাকে আপনার ডিজাইন অনুযায়ী সাজিয়ে নিন
        search = st.text_input("🔍 মেম্বার খুঁজুন (নাম বা আইডি)", placeholder="Search here...")
        if search:
            df_savings = df_savings[df_savings['Name'].astype(str).str.contains(search, case=False) | df_savings['ID'].astype(str).str.contains(search)]
        
        st.table(df_savings)
    else:
        st.info("গুগল শিটে কোনো ডাটা পাওয়া যায়নি।")
