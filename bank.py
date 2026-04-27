import streamlit as st
import pandas as pd
from datetime import datetime
import database as db 

# --- ১. ডাটাবেজ কানেকশন ও সর্টিং ---
def get_clean_fdr_data():
    conn = db.connect_db()
    if conn:
        try:
            ws = conn.worksheet("FDR_Data")
            data = ws.get_all_records()
            if not data: return []
            df = pd.DataFrame(data)
            # তারিখ অনুযায়ী সিরিয়াল করা
            df['temp_date'] = pd.to_datetime(df['Open_Date'], format='%m/%d/%y', errors='coerce')
            df = df.sort_values(by='temp_date', ascending=True)
            return df.to_dict('records')
        except: return []
    return []

def get_savings_data():
    conn = db.connect_db()
    if conn:
        try:
            ws = conn.worksheet("Bank_Savings")
            val = ws.cell(2, 1).value
            return float(val) if val else 0.0
        except: return 0.0
    return 0.0

# --- ২. FDR অ্যাড করার ডায়ালগ (এরর-ফ্রি) ---
@st.dialog("➕ ADD NEW FDR")
def open_fdr_form():
    st.write("### FDR Entry Form")
    f_url = st.text_input("Bank Receipt Link")
    f_amt = st.number_input("Amount", min_value=0.0)
    f_date = st.date_input("Date", datetime.now())
    if st.button("SAVE"):
        conn = db.connect_db()
        ws = conn.worksheet("FDR_Data")
        ws.append_row([len(ws.get_all_values()), f_date.strftime('%m/%d/%y'), "", f_amt, "Active", f_url])
        st.rerun()

# --- ৩. মেইন শো ফাঞ্চন (ইউনিক সিরিয়াল গ্রিড) ---
def show():
    user_role = st.session_state.get("role", "Member")
    
    # লাক্সারি ডিজাইন CSS
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A; }
        .main-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 15px; padding: 20px; border-left: 5px solid #38BDF8;
            text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.3); margin-bottom: 20px;
        }
        .month-text { color: #38BDF8; font-size: 20px; font-weight: bold; }
        .amt-text { color: white; font-size: 24px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;'>🏦 BANKING MANAGEMENT</h1>", unsafe_allow_html=True)

    # ডাটা লোড করা
    savings_bal = get_savings_data()
    fdr_list = get_clean_fdr_data()
    total_fdr = sum(float(str(r['Amount']).replace(',','')) for r in fdr_list)

    tab1, tab2, tab3 = st.tabs(["🏠 OVERVIEW", "📅 FDR GRID", "🏦 SAVINGS"])

    # OVERVIEW: যেখানে আগে ডাটা গায়েব ছিল
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="main-card"><p style="color:#94A3B8;">SAVINGS</p><p class="amt-text">৳ {savings_bal:,.2f}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="main-card" style="border-left-color:#8B5CF6;"><p style="color:#94A3B8;">TOTAL FDR</p><p class="amt-text">৳ {total_fdr:,.2f}</p></div>', unsafe_allow_html=True)

    # FDR GRID: সিরিয়াল অনুযায়ী
    with tab2:
        if user_role == "Admin":
            if st.button("➕ ADD FDR"): open_fdr_form()
        
        if fdr_list:
            cols = st.columns(3)
            for i, row in enumerate(fdr_list):
                try:
                    dt = datetime.strptime(str(row['Open_Date']), '%m/%d/%y')
                    month, year = dt.strftime("%B"), dt.strftime("%Y")
                except: month, year = "N/A", ""
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="main-card">
                            <div class="month-text">{month}</div>
                            <div style="color:#94A3B8; font-size:12px;">{year}</div>
                            <div class="amt-text" style="font-size:20px;">৳ {float(row['Amount']):,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if row['Link']: st.link_button("🌐 VIEW", row['Link'], use_container_width=True)

    # SAVINGS: ডাটা আপডেট করার অপশন
    with tab3:
        st.markdown(f'<div class="main-card"><p class="amt-text">Current: ৳ {savings_bal:,.2f}</p></div>', unsafe_allow_html=True)
        if user_role == "Admin":
            new_val = st.number_input("Update Savings Balance", value=float(savings_bal))
            if st.button("CONFIRM UPDATE"):
                conn = db.connect_db()
                conn.worksheet("Bank_Savings").update_cell(2, 1, new_val)
                st.success("Updated!")
                st.rerun()
