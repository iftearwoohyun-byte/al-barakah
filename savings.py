import streamlit as st
import pandas as pd
import database as db 
from datetime import datetime

@st.dialog("Collect Savings")
def add_deposit():
    st.markdown("<h3 style='color:#1A365D;'>নতুন সঞ্চয় জমা করুন</h3>", unsafe_allow_html=True)
    members_data = db.get_live_data() # লাইভ ডাটা কল
    
    if not members_data:
        st.error("মেম্বার লিস্ট পাওয়া যায়নি।")
        return

    names = [f"{m['Name']} (ID: {m['ID']})" for m in members_data]
    selected_member = st.selectbox("মেম্বার সিলেক্ট করুন", names)
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    selected_month = st.selectbox("মাস সিলেক্ট করুন", months)
    selected_year = st.selectbox("বছর", ["2025", "2026", "2027"])
    
    m_id = selected_member.split("(ID: ")[1].replace(")", "")
    member = next((m for m in members_data if str(m['ID']) == m_id), None)
    default_amt = int(member.get('Share', 1)) * 5000 if member else 0
    
    amount = st.text_input("জমার পরিমাণ", value=str(default_amt))

    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        today = datetime.now().strftime("%d/%m/%Y")
        row = [today, m_id, member['Name'], amount, selected_month, selected_year]
        
        if db.add_savings(row):
            st.success("গুগল শিটে সেভ হয়েছে!")
            st.rerun()
        else:
            st.error("সেভ হতে সমস্যা হয়েছে।")

def show():
    st.markdown('<h1 style="text-align:center; color:#1A365D;">AL-BARAKAH SAVINGS LEDGER</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕\nADD SAVINGS"):
            add_deposit()

    # শিট থেকে জমা হওয়া ডাটা দেখানো
    sheet = db.connect_db()
    if sheet:
        savings_df = pd.DataFrame(sheet.worksheet("Savings").get_all_records())
        if not savings_df.empty:
            st.table(savings_df.tail(10)) # সর্বশেষ ১০টি এন্ট্রি
        else:
            st.info("কোনো সঞ্চয়ের ডাটা পাওয়া যায়নি।")
