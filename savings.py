import streamlit as st
import pandas as pd
import database as db 
from datetime import datetime

def load_all_savings():
    sheet = db.connect_db()
    if sheet:
        try:
            worksheet = sheet.worksheet("Savings")
            data = worksheet.get_all_records()
            return data, worksheet
        except Exception as e:
            st.error(f"Error loading sheet: {e}")
            return [], None
    return [], None

@st.dialog("Collect Savings")
def add_deposit():
    st.markdown("<h3 style='color:#1A365D;'>নতুন সঞ্চয় ও জরিমানা জমা</h3>", unsafe_allow_html=True)
    members_data = db.get_live_data() 
    
    if not members_data:
        st.error("মেম্বার লিস্ট পাওয়া যায়নি!")
        return

    names = [f"{m['Name']} (ID: {m['ID']})" for m in members_data]
    selected_member = st.selectbox("মেম্বার সিলেক্ট করুন", names)
    
    # আপনার শিটের কলাম অনুযায়ী মাস
    months = ["Nov_25", "Dec_25", "Jan_26", "Feb_26", "Mar_26", "Apr_26", "May_26", "Jun_26", "Jul_26", "Aug_26", "Sep_26", "Oct_26"]
    selected_month = st.selectbox("মাস সিলেক্ট করুন", months)
    
    m_id = selected_member.split("(ID: ")[1].replace(")", "")
    member = next((m for m in members_data if str(m['ID']) == m_id), None)
    
    # জমার টাকা এবং জরিমানা আলাদা ইনপুট
    default_amt = int(member.get('Share', 1)) * 5000 if member else 5000
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("সঞ্চয় জমা (টাকা)", value=default_amt, step=500)
    with col2:
        fine = st.number_input("জরিমানা/Late Fee", value=0, step=10)

    total_to_save = amount + fine

    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        data, worksheet = load_all_savings()
        if worksheet:
            try:
                all_ids = worksheet.col_values(1)
                row_index = all_ids.index(str(m_id)) + 1
                headers = worksheet.row_values(1)
                col_index = headers.index(selected_month) + 1
                
                # মোট টাকা (জমা + জরিমানা) আপডেট করা
                worksheet.update_cell(row_index, col_index, total_to_save)
                
                st.success(f"সফলভাবে {total_to_save} টাকা (জরিমানাসহ) সেভ হয়েছে!")
                st.rerun()
            except:
                st.error("শিটে ডাটা আপডেট করতে সমস্যা হয়েছে।")

def show():
    st.markdown("""
        <style>
        .savings-header { background-color: #1A365D; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
        .header-text { color: white !important; font-family: 'Segoe UI'; font-weight: bold; font-size: 24px; }
        thead tr th { background-color: #4A5568 !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="savings-header"><h1 class="header-text">AL-BARAKAH SAVINGS LEDGER</h1></div>', unsafe_allow_html=True)

    if st.button("➕ ADD SAVINGS & FINE", key="add_sav_btn"):
        add_deposit()
    
    st.markdown("<br>", unsafe_allow_html=True)

    savings_data, _ = load_all_savings()
    
    if savings_data:
        df = pd.DataFrame(savings_data)
        month_cols = ["Nov_25", "Dec_25", "Jan_26", "Feb_26", "Mar_26", "Apr_26", "May_26", "Jun_26", "Jul_26", "Aug_26", "Sep_26", "Oct_26"]
        
        table_rows = []
        for index, row in df.iterrows():
            total_bal = 0
            last_paid_month = "No Payment"
            
            # মাস কলামগুলো চেক করে Last Paid Month বের করা
            for m in month_cols:
                if m in row and row[m] != "" and row[m] != 0:
                    try:
                        val = float(row[m])
                        total_bal += val
                        last_paid_month = m.replace("_", " ") # যেমন: Jan 26
                    except: continue
            
            table_rows.append({
                "ID": f"{int(row['ID']):03d}",
                "Member Name": row['Name'],
                "Last Paid Month": last_paid_month,
                "Total Balance": f"{total_bal:,.2f}"
            })

        display_df = pd.DataFrame(table_rows)
        search = st.text_input("🔍 মেম্বার খুঁজুন", placeholder="নাম বা আইডি...")
        if search:
            display_df = display_df[display_df['Member Name'].str.contains(search, case=False) | display_df['ID'].astype(str).str.contains(search)]

        st.table(display_df)
    else:
        st.info("গুগল শিটে কোনো ডাটা নেই।")
