import streamlit as st
import pandas as pd
from datetime import datetime
import database as db 

# --- ১. মাস ও সাল বের করার ফাংশন ---
def get_fdr_month_year(date_str):
    try:
        # গুগল শিট থেকে আসা তারিখ (MM/DD/YY) ফরম্যাট হ্যান্ডেল করা
        dt = datetime.strptime(str(date_str), '%m/%d/%y')
        return dt.strftime("%B"), dt.strftime("%Y")
    except:
        return "N/A", "N/A"

# --- ২. ডাটাবেজ ফাংশন ---
def get_savings_bal():
    conn = db.connect_db()
    if conn:
        try:
            ws = conn.worksheet("Bank_Savings")
            return float(ws.cell(2, 1).value or 0)
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

# --- ৩. FDR ফর্ম ---
@st.dialog("➕ ADD NEW FDR")
def open_add_fdr_form():
    st.write("### NEW FDR ENTRY")
    fdr_url = st.text_input("Bank Link (URL)")
    amount = st.number_input("Amount (BDT)", min_value=0.0)
    o_date = st.date_input("Opening Date", datetime.now())
    m_date = st.date_input("Maturity Date", datetime.now())
    status = st.selectbox("Status", ["Active", "Matured"])
    
    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        conn = db.connect_db()
        if conn:
            ws = conn.worksheet("FDR_Data")
            ws.append_row([len(ws.get_all_values()), o_date.strftime('%m/%d/%y'), 
                          m_date.strftime('%m/%d/%y'), amount, status, fdr_url])
            st.success("Saved Successfully!")
            st.rerun()

# --- ৪. মেইন ইউনিক ডিজাইন ---
def show():
    user_role = st.session_state.get("role", "Member")
    
    # লাক্সারি ডার্ক গোল্ডেন থিম CSS
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A; }
        .fdr-card {
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid #334155;
            text-align: center;
            transition: 0.3s;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.4);
            margin-bottom: 20px;
        }
        .fdr-card:hover { border-color: #38BDF8; transform: translateY(-5px); }
        .month-text { color: #38BDF8; font-size: 18px; font-weight: bold; text-transform: uppercase; margin-bottom: 0px; }
        .year-text { color: #94A3B8; font-size: 14px; margin-bottom: 10px; }
        .amount-text { color: #F8FAFC; font-size: 22px; font-weight: 800; margin: 10px 0; }
        .status-badge {
            padding: 4px 12px;
            border-radius: 50px;
            font-size: 10px;
            font-weight: bold;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; color:#38BDF8;'>🏦 SOCIETY BANKING</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏠 DASHBOARD", "💰 FDR GRID", "🏦 SAVINGS"])

    with tab1:
        bal = get_savings_bal()
        fdr_data = get_fdr_list()
        fdr_total = sum(float(r['Amount']) for r in fdr_data) if fdr_data else 0.0
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="fdr-card"><div class="year-text">SAVINGS BALANCE</div><div class="amount-text">৳ {bal:,.2f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="fdr-card" style="border-top: 4px solid #8B5CF6;"><div class="year-text">TOTAL FDR</div><div class="amount-text">৳ {fdr_total:,.2f}</div></div>', unsafe_allow_html=True)

    with tab2:
        col_t, col_b = st.columns([3, 1])
        with col_t: st.markdown("### 🏦 Active FDR Records")
        with col_b:
            if user_role == "Admin":
                if st.button("➕ ADD NEW"): open_add_fdr_form()

        fdr_list = get_fdr_list()
        if not fdr_list:
            st.info("No FDR data found in Google Sheets.")
        else:
            cols = st.columns(3)
            for i, row in enumerate(fdr_list):
                month, year = get_fdr_month_year(row['Open_Date'])
                st_color = "#10B981" if row['Status'] == "Active" else "#F59E0B"
                bg_status = "#064E3B" if row['Status'] == "Active" else "#78350F"
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="fdr-card">
                            <div class="month-text">{month}</div>
                            <div class="year-text">{year}</div>
                            <hr style="border: 0.5px solid #334155; margin: 10px 0;">
                            <div class="amount-text">৳ {float(row['Amount']):,.0f}</div>
                            <div class="status-badge" style="background:{bg_status}; color:{st_color};">
                                ● {row['Status'].upper()}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # বাটন গ্রুপ
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if row['Link']: st.link_button("🌐 VIEW", row['Link'], use_container_width=True)
                    with btn_col2:
                        if user_role == "Admin":
                            if st.button("🗑️", key=f"del_{i}", use_container_width=True):
                                conn = db.connect_db()
                                ws = conn.worksheet("FDR_Data")
                                # ID দিয়ে রো মুছে ফেলা
                                cells = ws.findall(str(row['ID']))
                                for cell in cells:
                                    if cell.col == 1:
                                        ws.delete_rows(cell.row)
                                        st.rerun()

    with tab3:
        bal = get_savings_bal()
        st.markdown(f'<div class="fdr-card" style="max-width:400px; margin:auto;"><div class="year-text">CURRENT BALANCE</div><div class="amount-text" style="color:#38BDF8;">৳ {bal:,.2f}</div></div>', unsafe_allow_html=True)
        if user_role == "Admin":
            st.write("---")
            new_bal = st.number_input("Enter Updated Amount", value=float(bal))
            if st.button("CONFIRM UPDATE", type="primary", use_container_width=True):
                conn = db.connect_db()
                conn.worksheet("Bank_Savings").update_cell(2, 1, new_bal)
                st.success("Balance Updated!")
                st.rerun()
