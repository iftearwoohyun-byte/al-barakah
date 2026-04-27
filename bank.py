import streamlit as st
import pandas as pd
from datetime import datetime
import database as db  # আপনার গুগল শিট কানেকশন ফাইল

# --- ১. ডাটাবেজ ফাংশন (গুগল শিট এডাপ্টেশন) ---
def get_savings_bal():
    conn = db.connect_db()
    if conn:
        try:
            worksheet = conn.worksheet("Bank_Savings")
            val = worksheet.cell(2, 1).value # ২য় সারি, ১ম কলাম থেকে ব্যালেন্স নেবে
            return float(val) if val else 0.0
        except: return 0.0
    return 0.0

def get_fdr_list():
    conn = db.connect_db()
    if conn:
        try:
            worksheet = conn.worksheet("FDR_Data")
            data = worksheet.get_all_records()
            # লিস্ট ফরম্যাটে রিটার্ন করা হচ্ছে যাতে আপনার লুপে সমস্যা না হয়
            return [[r['ID'], r['Open_Date'], r['Mature_Date'], r['Amount'], r['Status'], r['Link']] for r in data]
        except: return []
    return []

# --- ২. FDR ফর্ম (গুগল শিট কানেকশনসহ) ---
@st.dialog("➕ ADD NEW FDR")
def open_add_fdr_form():
    st.write("### NEW FDR ENTRY")
    o_date = st.date_input("Opening Date", datetime.now())
    m_date = st.date_input("Maturity Date", datetime.now())
    amount = st.number_input("Amount (Taka)", min_value=0.0, step=500.0)
    link = st.text_input("Online Bank Link (URL)")
    status = st.selectbox("Status", ["Active", "Matured"])
    
    if st.button("SAVE RECORD", type="primary", use_container_width=True):
        conn = db.connect_db()
        if conn:
            worksheet = conn.worksheet("FDR_Data")
            new_id = len(worksheet.get_all_values())
            worksheet.append_row([
                new_id, 
                o_date.strftime('%m/%d/%y'), 
                m_date.strftime('%m/%d/%y'), 
                amount, 
                status, 
                link
            ])
            st.success("FDR Saved to Google Sheet!")
            st.rerun()

# --- ৩. মেইন শো ফাংশন (ডিজাইন অপরিবর্তিত) ---
def show():
    user_role = st.session_state.get("role", "Member")
    
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A; }
        h1, h2, h3 { color: #38BDF8 !important; text-align: center; font-family: 'Segoe UI'; }
        .card-container { display: flex; justify-content: center; gap: 20px; margin-top: 30px; }
        .bank-card { background-color: #1E293B; padding: 30px; border-radius: 15px; text-align: center; border-top: 5px solid #38BDF8; min-width: 250px; box-shadow: 0 10px 15px rgba(0,0,0,0.3); }
        .card-title { color: #94A3B8; font-size: 14px; margin-bottom: 10px; }
        .card-value { color: white; font-size: 28px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>SOCIETY BANKING SYSTEM</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏠 HOME", "💰 FDR LIST", "🏦 SAVINGS"])

    with tab1:
        fdr_list = get_fdr_list()
        fdr_total = sum(float(r[3]) for r in fdr_list)
        st.markdown(f"""
            <div class="card-container">
                <div class="bank-card">
                    <div class="card-title">🏦 SAVINGS BALANCE</div>
                    <div class="card-value">৳ {get_savings_bal():,.2f}</div>
                </div>
                <div class="bank-card" style="border-top-color: #8B5CF6;">
                    <div class="card-title">💰 TOTAL FDR</div>
                    <div class="card-value">৳ {fdr_total:,.2f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with tab2:
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1: st.write("### FDR Grid View")
        
        with col_h2: 
            if user_role == "Admin":
                if st.button("➕ ADD FDR", use_container_width=True):
                    open_add_fdr_form()
            else:
                st.info("View Only Mode")

        fdr_list = get_fdr_list()
        if not fdr_list:
            st.info("No FDR records found in Google Sheets.")
        else:
            cols = st.columns(3)
            for i, row in enumerate(fdr_list):
                with cols[i % 3]:
                    try:
                        dt = datetime.strptime(str(row[1]), '%m/%d/%y')
                        month_year = dt.strftime("%B'%y")
                    except: month_year = row[1]
                    
                    status_color = "#10B981" if row[4] == "Active" else "#F59E0B"
                    
                    with st.container(border=True):
                        st.markdown(f"**{month_year}**")
                        st.markdown(f"### ৳ {float(row[3]):,.0f}")
                        st.markdown(f"<span style='color:{status_color}; font-weight:bold;'>{str(row[4]).upper()}</span>", unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if row[5]: st.link_button("🌐 Open", row[5])
                        
                        with c2:
                            if user_role == "Admin":
                                if st.button("🗑️", key=f"del_{row[0]}", help="Delete"):
                                    conn = db.connect_db()
                                    ws = conn.worksheet("FDR_Data")
                                    # ID খুঁজে বের করে রো ডিলিট করা
                                    cells = ws.findall(str(row[0]))
                                    for cell in cells:
                                        if cell.col == 1:
                                            ws.delete_rows(cell.row)
                                            st.rerun()

    with tab3:
        st.write("### Update Savings Balance")
        current_bal = get_savings_bal()
        
        st.markdown(f"""
            <div class="bank-card" style="margin: auto; width: 50%;">
                <div class="card-title">Current Savings Balance</div>
                <div class="card-value" style="color:#38BDF8;">৳ {current_bal:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if user_role == "Admin":
            st.write("<br>", unsafe_allow_html=True)
            new_bal = st.number_input("Enter New Balance", value=float(current_bal))
            
            if st.button("CONFIRM UPDATE", type="primary", use_container_width=True):
                conn = db.connect_db()
                if conn:
                    worksheet = conn.worksheet("Bank_Savings")
                    worksheet.update_cell(2, 1, new_bal) # ২য় সারি ১ম কলামে আপডেট হবে
                    st.success("Balance Updated in Google Sheet!")
                    st.rerun()
        else:
            st.warning("⚠️ Access Restricted: Only Admin can update savings balance.")
