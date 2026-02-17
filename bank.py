import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- ১. ডাটাবেজ ফাংশন (হুবহু আগের মতো) ---
DB_NAME = "somiti_ultimate_v5.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS fdr_data 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, open_date TEXT, mature_date TEXT, 
                   amount REAL, status TEXT, link TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS savings_data (balance REAL)''')
    cur.execute("SELECT COUNT(*) FROM savings_data")
    if cur.fetchone()[0] == 0: 
        cur.execute("INSERT INTO savings_data VALUES (0.0)")
    conn.commit()
    conn.close()

def get_savings_bal():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT balance FROM savings_data")
    bal = cur.fetchone()[0]
    conn.close()
    return bal

def get_fdr_list():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM fdr_data ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()
    return data

# --- ২. FDR ফর্ম (অ্যাডমিন শুধুমাত্র ব্যবহার করবে) ---
@st.dialog("➕ ADD NEW FDR")
def open_add_fdr_form():
    st.write("### NEW FDR ENTRY")
    o_date = st.date_input("Opening Date", datetime.now())
    m_date = st.date_input("Maturity Date", datetime.now())
    amount = st.number_input("Amount (Taka)", min_value=0.0, step=500.0)
    link = st.text_input("Online Bank Link (URL)")
    status = st.selectbox("Status", ["Active", "Matured"])
    
    if st.button("SAVE RECORD", type="primary", use_container_width=True):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO fdr_data (open_date, mature_date, amount, status, link) VALUES (?,?,?,?,?)",
                    (o_date.strftime('%m/%d/%y'), m_date.strftime('%m/%d/%y'), amount, status, link))
        conn.commit()
        conn.close()
        st.success("FDR Saved Successfully!")
        st.rerun()

# --- ৩. মেইন শো ফাংশন (শর্ত সহ আপডেট করা) ---
def show():
    init_db()
    
    # সেশন স্টেট থেকে রোল চেক করা
    user_role = st.session_state.get("role", "Member")
    
    # লাক্সারি ডার্ক থিম CSS (হুবহু আগের মতো)
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

    # ড্যাশবোর্ড মেনু
    tab1, tab2, tab3 = st.tabs(["🏠 HOME", "💰 FDR LIST", "🏦 SAVINGS"])

    # --- HOME TAB (সবাই দেখতে পাবে) ---
    with tab1:
        fdr_total = sum(r[3] for r in get_fdr_list())
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

    # --- FDR LIST TAB ---
    with tab2:
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1: st.write("### FDR Grid View")
        
        # শর্ত: শুধুমাত্র এডমিন FDR যোগ করতে পারবে
        with col_h2: 
            if user_role == "Admin":
                if st.button("➕ ADD FDR", use_container_width=True):
                    open_add_fdr_form()
            else:
                st.info("View Only Mode")

        fdr_list = get_fdr_list()
        cols = st.columns(3)
        
        for i, row in enumerate(fdr_list):
            with cols[i % 3]:
                try:
                    dt = datetime.strptime(row[1], '%m/%d/%y')
                    month_year = dt.strftime("%B'%y")
                except: month_year = row[1]
                
                status_color = "#10B981" if row[4] == "Active" else "#F59E0B"
                
                with st.container(border=True):
                    st.markdown(f"**{month_year}**")
                    st.markdown(f"### ৳ {row[3]:,.0f}")
                    st.markdown(f"<span style='color:{status_color}; font-weight:bold;'>{row[4].upper()}</span>", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if row[5]: st.link_button("🌐 Open", row[5])
                    
                    # শর্ত: শুধুমাত্র এডমিন ডিলিট বাটন দেখতে পাবে
                    with c2:
                        if user_role == "Admin":
                            if st.button("🗑️", key=f"del_{row[0]}", help="Delete this FDR"):
                                conn = sqlite3.connect(DB_NAME)
                                cur = conn.cursor()
                                cur.execute("DELETE FROM fdr_data WHERE id=?", (row[0],))
                                conn.commit(); conn.close()
                                st.rerun()

    # --- SAVINGS TAB ---
    with tab3:
        st.write("### Update Savings Balance")
        current_bal = get_savings_bal()
        
        st.markdown(f"""
            <div class="bank-card" style="margin: auto; width: 50%;">
                <div class="card-title">Current Savings Balance</div>
                <div class="card-value" style="color:#38BDF8;">৳ {current_bal:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # শর্ত: শুধুমাত্র এডমিন ব্যালেন্স আপডেট করতে পারবে
        if user_role == "Admin":
            st.write("<br>", unsafe_allow_html=True)
            new_bal = st.number_input("Enter New Balance", value=current_bal)
            
            if st.button("CONFIRM UPDATE", type="primary", use_container_width=True):
                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()
                cur.execute("UPDATE savings_data SET balance=?", (new_bal,))
                conn.commit(); conn.close()
                st.success("Balance Updated!")
                st.rerun()
        else:
            st.warning("⚠️ Access Restricted: Only Admin can update savings balance.")
