import streamlit as st
import pandas as pd
from datetime import datetime
import database as db 

# --- ১. তারিখ অনুযায়ী সিরিয়াল করার ফাংশন ---
def get_sorted_fdr_list():
    conn = db.connect_db()
    if conn:
        try:
            ws = conn.worksheet("FDR_Data")
            data = ws.get_all_records()
            if not data: return []
            
            df = pd.DataFrame(data)
            # তারিখ ফরম্যাট ঠিক করে সর্টিং করা (সিরিয়াল বজায় রাখা)
            df['temp_date'] = pd.to_datetime(df['Open_Date'], format='%m/%d/%y', errors='coerce')
            df = df.sort_values(by='temp_date', ascending=True)
            return df.to_dict('records')
        except: return []
    return []

def format_fdr_date(date_str):
    try:
        dt = datetime.strptime(str(date_str), '%m/%d/%y')
        return dt.strftime("%B"), dt.strftime("%Y")
    except: return "N/A", "N/A"

# --- ২. FDR যোগ করার ডায়ালগ ---
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
            try:
                ws = conn.worksheet("FDR_Data")
                # নতুন আইডি জেনারেট করা
                new_id = len(ws.get_all_values())
                ws.append_row([new_id, o_date.strftime('%m/%d/%y'), m_date.strftime('%m/%d/%y'), amount, status, fdr_url])
                st.success("Saved Successfully!")
                st.rerun()
            except: st.error("FDR_Data শিটটি খুঁজে পাওয়া যায়নি!")

# --- ৩. মেইন শো ফাংশন (ইউনিক গ্রিড ডিজাইন) ---
def show():
    user_role = st.session_state.get("role", "Member")
    
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A; }
        .fdr-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 15px;
            padding: 20px;
            border-left: 5px solid #38BDF8;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        .month-label { color: #38BDF8; font-size: 20px; font-weight: bold; margin-bottom: 0px; }
        .year-label { color: #94A3B8; font-size: 14px; margin-bottom: 10px; }
        .amt-label { color: #FFFFFF; font-size: 24px; font-weight: bold; margin: 10px 0; }
        .status-tag { font-size: 11px; font-weight: bold; padding: 3px 10px; border-radius: 20px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;'>🏦 BANKING SYSTEM</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏠 OVERVIEW", "📅 FDR GRID", "🏦 SAVINGS"])

    sorted_fdr = get_sorted_fdr_list()

    with tab1:
        fdr_total = sum(float(str(r['Amount']).replace(',','')) for r in sorted_fdr) if sorted_fdr else 0.0
        # ড্যাশবোর্ড কার্ড (আপনার লেটেস্ট স্ক্রিনশটের মতো ডিজাইন)
        st.markdown(f'<div class="fdr-card"><div class="year-label">TOTAL FDR</div><div class="amt-label">৳ {fdr_total:,.2f}</div></div>', unsafe_allow_html=True)

    with tab2:
        col1, col2 = st.columns([3, 1])
        with col1: st.write("### FDR Serial by Month")
        with col2:
            if user_role == "Admin":
                if st.button("➕ NEW"): open_add_fdr_form()

        if not sorted_fdr:
            st.info("No FDR records found.")
        else:
            cols = st.columns(3)
            for i, row in enumerate(sorted_fdr):
                month, year = format_fdr_date(row['Open_Date'])
                st_color = "#10B981" if row['Status'] == "Active" else "#F59E0B"
                st_bg = "#064E3B" if row['Status'] == "Active" else "#78350F"
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="fdr-card">
                            <div class="month-label">{month}</div>
                            <div class="year-label">{year}</div>
                            <div class="amt-label">৳ {float(row['Amount']):,.0f}</div>
                            <span class="status-tag" style="background:{st_bg}; color:{st_color};">● {row['Status'].upper()}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        if row['Link']: st.link_button("🌐 VIEW", row['Link'], use_container_width=True)
                    with b2:
                        if user_role == "Admin":
                            if st.button("🗑️", key=f"del_{row['ID']}", use_container_width=True):
                                conn = db.connect_db()
                                ws = conn.worksheet("FDR_Data")
                                cell = ws.find(str(row['ID']))
                                if cell:
                                    ws.delete_rows(cell.row)
                                    st.rerun()

    with tab3:
        # Savings ব্যালেন্স আপডেট লজিক
        st.write("### Savings Management")
