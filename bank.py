import streamlit as st
import pandas as pd
from datetime import datetime
import database as db 

# স্ক্র্যাপিং লাইব্রেরি ইমপোর্ট (এরর হ্যান্ডলিং সহ)
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False

# --- ১. অটো ডাটা রিড লজিক ---
def fetch_fdr_details(url):
    if not SCRAPER_AVAILABLE: return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # ট্রাস্ট ব্যাংক রিসিট থেকে অ্যামাউন্ট খোঁজা (নমুনা লজিক)
            page_text = soup.get_text()
            if "Amount" in page_text:
                # এটি একটি সিম্পল উদাহরণ, ব্যাংকের পেজ অনুযায়ী ডাটা ক্লিন করা হবে
                return {"amount": 0.0} 
        return None
    except: return None

# --- ২. ডাটাবেজ ফাংশন ---
def get_savings_bal():
    conn = db.connect_db()
    if conn:
        try:
            ws = conn.worksheet("Bank_Savings")
            val = ws.cell(2, 1).value
            return float(val) if val else 0.0
        except: return 0.0
    return 0.0

def get_fdr_list():
    conn = db.connect_db()
    if conn:
        try:
            ws = conn.worksheet("FDR_Data")
            return ws.get_all_records()
        except: return []
    return []

# --- ৩. FDR ফর্ম (ডিজাইন একদম আপনার অরিজিনাল) ---
@st.dialog("➕ ADD NEW FDR")
def open_add_fdr_form():
    st.write("### NEW FDR ENTRY")
    fdr_url = st.text_input("Paste Bank Link (URL)")
    
    if st.button("🔍 AUTO FILL FROM LINK", use_container_width=True):
        if fdr_url:
            with st.spinner("Fetching data..."):
                details = fetch_fdr_details(fdr_url)
                if details:
                    st.session_state['temp_amt'] = details['amount']
                    st.success("Data loaded!")
                else:
                    st.error("Could not auto-read. Enter manually.")
    
    amount = st.number_input("Amount (BDT)", value=st.session_state.get('temp_amt', 0.0))
    o_date = st.date_input("Opening Date", datetime.now())
    m_date = st.date_input("Maturity Date", datetime.now())
    status = st.selectbox("Status", ["Active", "Matured"])
    
    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        conn = db.connect_db()
        if conn:
            try:
                ws = conn.worksheet("FDR_Data")
                ws.append_row([len(ws.get_all_values()), o_date.strftime('%m/%d/%y'), 
                              m_date.strftime('%m/%d/%y'), amount, status, fdr_url])
                if 'temp_amt' in st.session_state: del st.session_state['temp_amt']
                st.success("Saved!")
                st.rerun()
            except: st.error("Check Google Sheet tabs!")

# --- ৪. মেইন ড্যাশবোর্ড (হুবহু অরিজিনাল ডার্ক থিম) ---
def show():
    user_role = st.session_state.get("role", "Member")
    
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A; }
        h1, h3 { color: #38BDF8 !important; text-align: center; font-family: 'Segoe UI'; }
        .bank-card { background-color: #1E293B; padding: 25px; border-radius: 15px; text-align: center; border-top: 5px solid #38BDF8; box-shadow: 0 10px 15px rgba(0,0,0,0.3); margin-bottom: 20px;}
        .card-title { color: #94A3B8; font-size: 14px; margin-bottom: 5px; }
        .card-value { color: white; font-size: 26px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>SOCIETY BANKING SYSTEM</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏠 HOME", "💰 FDR LIST", "🏦 SAVINGS"])

    with tab1:
        bal = get_savings_bal()
        fdr_data = get_fdr_list()
        fdr_total = sum(float(r['Amount']) for r in fdr_data) if fdr_data else 0.0
        
        st.markdown(f"""
            <div class="bank-card">
                <div class="card-title">🏦 SAVINGS BALANCE</div>
                <div class="card-value">৳ {bal:,.2f}</div>
            </div>
            <div class="bank-card" style="border-top-color: #8B5CF6;">
                <div class="card-title">💰 TOTAL FDR</div>
                <div class="card-value">৳ {fdr_total:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with tab2:
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1: st.write("### FDR Records")
        with col_h2: 
            if user_role == "Admin":
                if st.button("➕ ADD FDR"): open_add_fdr_form()

        fdr_list = get_fdr_list()
        if not fdr_list: st.info("No records found.")
        else:
            cols = st.columns(3)
            for i, row in enumerate(fdr_list):
                with cols[i % 3]:
                    color = "#10B981" if row['Status'] == "Active" else "#F59E0B"
                    with st.container(border=True):
                        st.markdown(f"**৳ {float(row['Amount']):,.0f}**")
                        st.markdown(f"<small style='color:{color}'>{row['Status'].upper()}</small>", unsafe_allow_html=True)
                        if row['Link']: st.link_button("🌐 View", row['Link'])
                        if user_role == "Admin":
                            if st.button("🗑️", key=f"del_{i}"):
                                # ডিলিট লজিক এখানে
                                pass

    with tab3:
        bal = get_savings_bal()
        st.markdown(f'<div class="bank-card"><div class="card-value">৳ {bal:,.2f}</div></div>', unsafe_allow_html=True)
        if user_role == "Admin":
            new_bal = st.number_input("Update Balance", value=float(bal))
            if st.button("CONFIRM UPDATE", type="primary"):
                conn = db.connect_db()
                conn.worksheet("Bank_Savings").update_cell(2, 1, new_bal)
                st.success("Updated!")
                st.rerun()
