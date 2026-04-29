import streamlit as st
import os
import base64
import pandas as pd
from datetime import datetime
import database as db  # নিশ্চিত করুন আপনার ডাটাবেজ কানেকশন ফাইলটি আছে

def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def get_home_stats():
    conn = db.connect_db()
    stats = {"savings": 0, "fdr": 0, "last_fdr": "N/A", "fine": 0}
    if conn:
        try:
            # ১. মোট সঞ্চয় (Savings Sheet)
            ws_s = conn.worksheet("Savings")
            df_s = pd.DataFrame(ws_s.get_all_records())
            exclude = ['ID', 'Name', 'Shares', 'Total', 'Remarks', 'Fine']
            val_cols = [c for c in df_s.columns if c not in exclude]
            for col in val_cols:
                stats["savings"] += pd.to_numeric(df_s[col].astype(str).str.replace(',', ''), errors='coerce').sum()

            # ২. FDR এবং শেষ FDR মাস (FDR_Data Sheet)
            ws_f = conn.worksheet("FDR_Data")
            df_f = pd.DataFrame(ws_f.get_all_records())
            if not df_f.empty:
                stats["fdr"] = pd.to_numeric(df_f['Amount'].astype(str).str.replace(',', ''), errors='coerce').sum()
                # তারিখ অনুযায়ী সাজিয়ে সর্বশেষ মাস বের করা
                df_f['temp_date'] = pd.to_datetime(df_f['Open_Date'], format='%m/%d/%y', errors='coerce')
                last_date = df_f.sort_values(by='temp_date', ascending=False).iloc[0]['Open_Date']
                if last_date:
                    dt = datetime.strptime(str(last_date), '%m/%d/%y')
                    stats["last_fdr"] = dt.strftime("%B %Y")

            # ৩. মোট জরিমানা (Late Fee Sheet)
            ws_l = conn.worksheet("Late Fee")
            l_vals = ws_l.get_all_values()
            stats["fine"] = sum(float(str(v).replace(',', '')) for r in l_vals for v in r if str(v).replace('.', '').isdigit())
            
        except: pass
    return stats

def show():
    # ১. লোগো সেকশন (আপনার আগের কোড)
    if os.path.exists("logo.png"):
        img_base64 = get_image_base64("logo.png")
        st.markdown(f'<div style="display: flex; justify-content: center; padding-top: 20px;"><img src="data:image/png;base64,{img_base64}" style="width: 150px; border-radius: 10px;"></div>', unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center;'>🏢</h1>", unsafe_allow_html=True)

    # ২. টাইটেল
    st.markdown("<h1 style='text-align:center; color:white; margin-top: 10px;'>Welcome to Al-Barakah Management System</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ৩. ডাটা কার্ডস সেকশন (উপরের ৩টি কার্ড)
    col1, col2, col3 = st.columns(3)
    def card(title, value, color="#22c55e"):
        st.markdown(f"""
        <div style="background-color:#33475b; padding:25px; border-radius:12px; text-align:center; border: 1px solid #2d3e4b; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); margin-bottom:15px;">
            <h4 style="color:#a3b1bb; margin-bottom:10px; font-size: 16px;">{title}</h4>
            <h2 style="color:{color}; margin:0; font-size: 26px;">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col1: card("Active Members", "17")
    with col2: card("Total Shares", "20")
    with col3: card("Status", "Active")

    # --- ৪. নতুন স্ট্যাটিস্টিক্স সেকশন (নিচে) ---
    st.markdown("<h3 style='text-align:center; color:#38BDF8; margin-top:30px;'>📊 Financial Overview</h3>", unsafe_allow_html=True)
    
    data = get_home_stats()
    
    c1, c2 = st.columns(2)
    with c1:
        card("Total Savings", f"৳{data['savings']:,.0f}", "#38BDF8")
        card("Last FDR Date", data['last_fdr'], "#F59E0B")
    with c2:
        card("Total FDR Amount", f"৳{data['fdr']:,.0f}", "#8B5CF6")
        card("Total Late Fee", f"৳{data['fine']:,.0f}", "#EF4444")

    # ব্যাকগ্রাউন্ড ফিক্স
    st.markdown("<style>.stApp { background-color: #1c2b36 !important; }</style>", unsafe_allow_html=True)
