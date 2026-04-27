import streamlit as st
import pandas as pd
import database as db 
from datetime import datetime

def load_all_savings():
    sheet = db.connect_db()
    if sheet:
        try:
            # সরাসরি Savings ট্যাব থেকে সব ডাটা পড়া
            worksheet = sheet.worksheet("Savings")
            data = worksheet.get_all_records()
            return data, worksheet
        except Exception as e:
            st.error(f"Error loading sheet: {e}")
            return [], None
    return [], None

@st.dialog("Collect Savings")
def add_deposit():
    st.markdown("<h3 style='color:#1A365D;'>নতুন সঞ্চয় জমা করুন</h3>", unsafe_allow_html=True)
    members_data = db.get_live_data() 
    
    if not members_data:
        st.error("মেম্বার লিস্ট পাওয়া যায়নি!")
        return

    # মেম্বার লিস্ট তৈরি
    names = [f"{m['Name']} (ID: {m['ID']})" for m in members_data]
    selected_member = st.selectbox("মেম্বার সিলেক্ট করুন", names)
    
    # আপনার শিটের কলাম অনুযায়ী মাস (হুবহু শিটের নামের সাথে মিল থাকতে হবে)
    months = ["Nov_25", "Dec_25", "Jan_26", "Feb_26", "Mar_26", "Apr_26", "May_26", "Jun_26", "Jul_26", "Aug_26", "Sep_26", "Oct_26"]
    selected_month = st.selectbox("মাস সিলেক্ট করুন", months)
    
    m_id = selected_member.split("(ID: ")[1].replace(")", "")
    member = next((m for m in members_data if str(m['ID']) == m_id), None)
    
    # অটো টাকা ক্যালকুলেশন (শেয়ার * ৫০০০)
    default_amt = int(member.get('Share', 1)) * 5000 if member else 5000
    amount = st.text_input("জমার পরিমাণ", value=str(default_amt))

    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        data, worksheet = load_all_savings()
        if worksheet:
            try:
                # শিটে আইডি অনুযায়ী সঠিক রো (Row) খুঁজে বের করা
                all_ids = worksheet.col_values(1) # প্রথম কলাম IDs
                row_index = all_ids.index(str(m_id)) + 1
                
                # সঠিক মাস অনুযায়ী কলাম (Column) খুঁজে বের করা
                headers = worksheet.row_values(1)
                col_index = headers.index(selected_month) + 1
                
                # শিটে ডাটা আপডেট করা
                worksheet.update_cell(row_index, col_index, amount)
                
                st.success(f"সফলভাবে {selected_month} এর জমা সেভ হয়েছে!")
                st.rerun()
            except ValueError:
                st.error("মেম্বার আইডি বা মাসের কলাম শিটে খুঁজে পাওয়া যায়নি!")
            except Exception as e:
                st.error(f"সেভ করতে সমস্যা হয়েছে: {e}")

def show():
    # --- আপনার অরিজিনাল CSS ডিজাইন ---
    st.markdown("""
        <style>
        .savings-header { background-color: #1A365D; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
        .header-text { color: white !important; font-family: 'Segoe UI'; font-weight: bold; font-size: 24px; }
        div.savings-btn-group button {
            height: 80px !important; font-size: 18px !important; font-weight: bold !important;
            background-color: #2D3748 !important; color: white !important; border-radius: 10px !important;
        }
        thead tr th { background-color: #4A5568 !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="savings-header"><h1 class="header-text">AL-BARAKAH SAVINGS LEDGER</h1></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 6])
    with col1:
        if st.button("➕\nADD SAVINGS", key="add_sav_btn"):
            add_deposit()
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ডাটা টেবিল দেখানো
    savings_data, _ = load_all_savings()
    
    if savings_data:
        df = pd.DataFrame(savings_data)
        
        # ক্যালকুলেশন লজিক
        # মাস কলামগুলোর নাম দিন যেগুলো আপনি যোগ করতে চান
        month_cols = ["Nov_25", "Dec_25", "Jan_26", "Feb_26", "Mar_26", "Apr_26"] # আপনার শিট অনুযায়ী
        
        # টোটাল ব্যালেন্স বের করা
        for col in month_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['Total Balance'] = df[month_cols].sum(axis=1)
        
        # আপনার সুন্দর টেবিল ভিউ
        display_df = df[['ID', 'Name', 'Shares', 'Total Balance']].copy()
        display_df['Total Balance'] = display_df['Total Balance'].map('{:,.2f}'.format)
        
        search = st.text_input("🔍 মেম্বার খুঁজুন", placeholder="নাম বা আইডি...")
        if search:
            display_df = display_df[display_df['Name'].str.contains(search, case=False) | display_df['ID'].astype(str).str.contains(search)]

        st.table(display_df)
    else:
        st.info("গুগল শিটে কোনো সঞ্চয়ের ডাটা পাওয়া যায়নি।")
