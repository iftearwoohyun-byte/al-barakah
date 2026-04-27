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
        except: return [], None
    return [], None

@st.dialog("Collect Savings & Late Fee")
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
    selected_month = st.selectbox("কোন মাসের টাকা?", months)
    
    m_id = selected_member.split("(ID: ")[1].replace(")", "")
    member_name = selected_member.split(" (ID:")[0]
    member = next((m for m in members_data if str(m['ID']) == m_id), None)
    
    default_amt = int(member.get('Share', 1)) * 5000 if member else 5000
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("সঞ্চয় জমা (টাকা)", value=default_amt, step=500)
    with col2:
        fine = st.number_input("জরিমানা / Late Fee (টাকা)", value=0, step=50)

    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        conn = db.connect_db()
        if conn:
            try:
                # ১. মূল Savings শিটে শুধুমাত্র সঞ্চয় আপডেট
                ws_sav = conn.worksheet("Savings")
                all_ids = ws_sav.col_values(1)
                row_idx = all_ids.index(str(m_id)) + 1
                headers = ws_sav.row_values(1)
                col_idx = headers.index(selected_month) + 1
                ws_sav.update_cell(row_idx, col_idx, amount) # জরিমানা ছাড়া শুধু জমা

                # ২. Late Fee শিটে জরিমানার তথ্য আলাদাভাবে সেভ
                if fine > 0:
                    try:
                        ws_fine = conn.worksheet("Late Fee") # শিটের নাম হুবহু মিল থাকতে হবে
                        ws_fine.append_row([member_name, selected_month, fine])
                    except:
                        st.warning("গুগল শিটে 'Late Fee' নামে কোনো ট্যাব খুঁজে পাওয়া যায়নি!")

                st.success(f"সফলভাবে {amount} টাকা সঞ্চয় এবং {fine} টাকা জরিমানা আলাদাভাবে সেভ হয়েছে!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating database: {e}")

def show():
    # ডিজাইন কোড আপনার আগের মতোই থাকছে
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
        for _, row in df.iterrows():
            total_bal = 0
            last_month = "None"
            for m in month_cols:
                if m in row and row[m] != "" and row[m] != 0:
                    try:
                        total_bal += float(row[m])
                        last_month = m.replace("_", " ")
                    except: continue
            
            table_rows.append({
                "ID": f"{int(row['ID']):03d}",
                "Member Name": row['Name'],
                "Last Paid": last_month,
                "Total Savings": f"{total_bal:,.2f}"
            })

        st.table(pd.DataFrame(table_rows))
    else:
        st.info("গুগল শিটে কোনো ডাটা নেই।")
