import streamlit as st
import pandas as pd
import database as db  # গুগল শিট কানেকশন
from datetime import datetime

# --- ১. ডাটা লোড ফাংশন (এখন গুগল শিট থেকে আসবে) ---
def load_all_savings_from_sheet():
    sheet = db.connect_db()
    if sheet:
        try:
            worksheet = sheet.worksheet("Savings")
            return worksheet.get_all_records()
        except: return []
    return []

# --- ২. কিস্তি জমার পপ-আপ (ডিজাইন একদম আগের মতো) ---
@st.dialog("Collect Savings")
def add_deposit():
    st.markdown("<h3 style='color:#1A365D;'>নতুন সঞ্চয় জমা করুন</h3>", unsafe_allow_html=True)
    
    # মেম্বার ডাটা গুগল শিট থেকে আসবে
    members_data = db.get_live_data() 
    
    if not members_data:
        st.error("মেম্বার লিস্ট খালি! আগে মেম্বার যোগ করুন।")
        return

    names = [f"{m['Name']} (ID: {m['ID']})" for m in members_data]
    selected_member = st.selectbox("মেম্বার সিলেক্ট করুন", names)
    
    # মাস তৈরির লজিক (আপনার অরিজিনাল ২৫-২৭ সাল)
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
    
    amount = st.text_input("জমার পরিমাণ (৫,০০০/শেয়ার)", value=str(default_amt))

    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        today = datetime.now().strftime("%d/%m/%Y")
        # গুগল শিটে জমা করার জন্য রো তৈরি
        row = [today, m_id, member['Name'], amount, selected_month.split("_")[0], "20" + selected_month.split("_")[1]]
        
        if db.add_savings(row):
            st.success("সফলভাবে সেভ হয়েছে!")
            st.rerun()
        else:
            st.error("সেভ হতে সমস্যা হয়েছে!")

# --- ৩. মেইন শো ফাংশন (ডিজাইন ও CSS আপনার অরিজিনালটা) ---
def show():
    st.markdown("""
        <style>
        .savings-container { background-color: #F0F4F8; padding: 10px; border-radius: 10px; }
        .savings-header { background-color: #1A365D; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
        .header-text { color: white !important; font-family: 'Segoe UI'; font-weight: bold; margin: 0; font-size: 24px; }
        div.savings-btn-group button {
            height: 100px !important; font-size: 18px !important; font-weight: bold !important;
            background-color: #2D3748 !important; color: white !important; border-radius: 10px !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        thead tr th { background-color: #4A5568 !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="savings-header"><h1 class="header-text">AL-BARAKAH SAVINGS LEDGER (2025-2027)</h1></div>', unsafe_allow_html=True)

    st.markdown('<div class="savings-btn-group">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 4])
    
    with col1:
        if st.button("➕\nADD SAVINGS", key="add_sav_btn"):
            add_deposit()
            
    with col2:
        if st.button("🔄\nREFRESH", key="sync_sav_btn"):
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ৪. ডাটা টেবিল (আপনার আগের ক্যালকুলেশন লজিক)
    savings_list = load_all_savings_from_sheet()
    
    if savings_list:
        df_raw = pd.DataFrame(savings_list)
        
        # আপনার আগের লজিক অনুযায়ী টেবিল সাজানো
        table_rows = []
        # ইউনিক মেম্বারদের জন্য গ্রুপিং (শিটে মেম্বার রিপিট হতে পারে)
        unique_members = df_raw['ID'].unique()
        
        for m_id in unique_members:
            m_data = df_raw[df_raw['ID'] == m_id]
            total_bal = pd.to_numeric(m_data['Amount']).sum()
            last_p = m_data.iloc[-1]['Month'] + " " + str(m_data.iloc[-1]['Year'])
            
            table_rows.append({
                "ID": f"{int(m_id):03d}",
                "Member Name": m_data.iloc[-1]['Name'],
                "Last Paid": last_p,
                "Total Balance": f"{total_bal:,.2f}"
            })

        df = pd.DataFrame(table_rows)
        search = st.text_input("🔍 মেম্বার খুঁজুন (নাম বা আইডি)", placeholder="Search here...")
        if search:
            df = df[df['Member Name'].str.contains(search, case=False) | df['ID'].str.contains(search)]

        st.table(df) # আপনার অরিজিনাল স্ট্যাটিক টেবিল
    else:
        st.info("কোনো ডাটা পাওয়া যায়নি।")
