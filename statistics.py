import streamlit as st
import pandas as pd
from datetime import datetime
import database as db 

# --- ১. মাস ও সাল বের করার ফাংশন ---
def get_fdr_month_year(date_str):
    try:
        # তারিখ ফরম্যাট (MM/DD/YY) অনুযায়ী প্রসেস করা
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
            # ডুপ্লিকেট হেডার এরর এড়াতে pandas ব্যবহার করে ডাটা পড়া
            data = ws.get_all_values()
            if len(data) < 2: return []
            
            df = pd.DataFrame(data[1:], columns=data[0])
            
            # --- মাস অনুসারে সিরিয়াল করার লজিক ---
            if 'Open_Date' in df.columns:
                df['temp_date'] = pd.to_datetime(df['Open_Date'], format='%m/%d/%y', errors='coerce')
                # তারিখ অনুযায়ী ছোট থেকে বড় (পুরাতন থেকে নতুন) সাজানো
                df = df.sort_values(by='temp_date', ascending=True)
            
            return df.to_dict('records')
        except Exception as e:
            st.error(f"ডাটা পড়তে সমস্যা: {e}")
            return []
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
            try:
                ws = conn.worksheet("FDR_Data")
                # নতুন আইডি জেনারেট করে ডাটা সেভ করা
                ws.append_row([len(ws.get_all_values()), o_date.strftime('%m/%d/%y'), 
                              m_date.strftime('%m/%d/%y'), amount, status, fdr_url])
                st.success("Saved Successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"সেভ করতে সমস্যা: {e}")

# --- ৪. মেইন ডিজাইন (আপনার দেওয়া ডিজাইন হুবহু) ---
def show():
    user_role = st.session_state.get("role", "Member")
    
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
        # কমা বা টেক্সট হ্যান্ডেল করে টোটাল বের করা
        fdr_total = sum(float(str(r['Amount']).replace(',', '')) for r in fdr_data if str(r['Amount']).replace('.','').isdigit()) if fdr_data else 0.0
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="fdr-card"><div class="year-text">SAVINGS BALANCE</div><div class="amount-text">৳ {bal:,.2f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="fdr-card" style="border-top: 4px solid #8B5CF6;"><div class="year-text">TOTAL FDR</div><div class="amount-text">৳ {fdr_total:,.2f}</div></div>', unsafe_allow_html=True)

    with tab2:
        col_t, col_b = st.columns([3, 1])
        with col_t: st.markdown("### 🏦 Monthly FDR Serial")
        with col_b:
            if user_role == "Admin":
                if st.button("➕ ADD NEW"): open_add_fdr_form()

        fdr_list = get_fdr_list() # সর্ট করা ডাটা আসবে
        if not fdr_list:
            st.info("গুগল শিটে কোনো FDR ডাটা পাওয়া যায়নি।")
        else:
            cols = st.columns(3)
            for i, row in enumerate(fdr_list):
                month, year = get_fdr_month_year(row.get('Open_Date', ''))
                st_status = str(row.get('Status', 'Active'))
                st_color = "#10B981" if st_status == "Active" else "#F59E0B"
                bg_status = "#064E3B" if st_status == "Active" else "#78350F"
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="fdr-card">
                            <div class="month-text">{month}</div>
                            <div class="year-text">{year}</div>
                            <hr style="border: 0.5px solid #334155; margin: 10px 0;">
                            <div class="amount-text">৳ {float(str(row.get('Amount', 0)).replace(',', '')):,.0f}</div>
                            <div class="status-badge" style="background:{bg_status}; color:{st_color};">
                                ● {st_status.upper()}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        if row.get('Link'): st.link_button("🌐 VIEW", row['Link'], use_container_width=True)
                    with b2:
                        if user_role == "Admin":
                            if st.button("🗑️", key=f"del_{i}", use_container_width=True):
                                conn = db.connect_db()
                                ws = conn.worksheet("FDR_Data")
                                target = ws.find(str(row.get('ID', '')))
                                if target:
                                    ws.delete_rows(target.row)
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
