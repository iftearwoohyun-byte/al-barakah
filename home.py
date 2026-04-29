import streamlit as st
import os
import base64
import pandas as pd
from datetime import datetime
import database as db

# লোগো কনভার্ট ফাংশন
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

# ডাটা সংগ্রহের মূল ফাংশন
def get_home_stats():
    conn = db.connect_db()
    stats = {"savings": 0.0, "fdr": 0.0, "last_fdr": "N/A", "fine": 0.0}
    
    if conn:
        try:
            # ১. মোট সঞ্চয় (Savings)
            ws_s = conn.worksheet("Savings")
            s_data = ws_s.get_all_values()
            if len(s_data) > 1:
                df_s = pd.DataFrame(s_data[1:], columns=s_data[0])
                exclude = ['ID', 'Name', 'Shares', 'Total', 'Remarks', 'Fine']
                val_cols = [c for c in df_s.columns if c and c not in exclude]
                for col in val_cols:
                    stats["savings"] += pd.to_numeric(df_s[col].str.replace(',', ''), errors='coerce').sum()

            # ২. FDR এমাউন্ট ও শেষ তারিখ (FDR_Data)
            ws_f = conn.worksheet("FDR_Data")
            f_data = ws_f.get_all_values()
            if len(f_data) > 1:
                df_f = pd.DataFrame(f_data[1:], columns=f_data[0])
                stats["fdr"] = pd.to_numeric(df_f['Amount'].str.replace(',', ''), errors='coerce').sum()
                if 'Open_Date' in df_f.columns:
                    # বিভিন্ন তারিখ ফরমেট হ্যান্ডেল করা
                    df_f['dt'] = pd.to_datetime(df_f['Open_Date'], errors='coerce')
                    valid_dates = df_f.dropna(subset=['dt'])
                    if not valid_dates.empty:
                        last_date = valid_dates.sort_values('dt').iloc[-1]['dt']
                        stats["last_fdr"] = last_date.strftime("%B %Y")

            # ৩. মোট জরিমানা (Late Fee)
            try:
                ws_l = conn.worksheet("Late Fee")
                l_vals = ws_l.get_all_values()
                for row in l_vals:
                    for val in row:
                        try:
                            clean_v = str(val).replace(',', '').strip()
                            if clean_v: stats["fine"] += float(clean_v)
                        except: continue
            except: pass
            
        except Exception as e:
            # এরর হলে কনসোলে দেখাবে কিন্তু অ্যাপ থামবে না
            print(f"Stats Load Error: {e}")
            
    return stats

# মেইন ডিসপ্লে ফাংশন
def show():
    # স্টাইল সেটিং
    st.markdown("""
        <style>
        .stApp { background-color: #1c2b36 !important; }
        .stat-card {
            background-color: #33475b;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #2d3e4b;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            margin-bottom: 15px;
        }
        .stat-title { color: #a3b1bb; font-size: 14px; margin-bottom: 8px; }
        .stat-value { font-size: 24px; font-weight: bold; margin: 0; }
        </style>
    """, unsafe_allow_html=True)

    # লোগো
    logo_base64 = get_image_base64("logo.png")
    if logo_base64:
        st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/png;base64,{logo_base64}" style="width: 120px;"></div>', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center; color:white;'>Al-Barakah Management System</h2>", unsafe_allow_html=True)

    # টপ কার্ডস (স্ট্যাটিক)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="stat-card"><p class="stat-title">Active Members</p><p class="stat-value" style="color:#22c55e;">17</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="stat-card"><p class="stat-title">Total Shares</p><p class="stat-value" style="color:#22c55e;">20</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="stat-card"><p class="stat-title">Status</p><p class="stat-value" style="color:#22c55e;">Active</p></div>', unsafe_allow_html=True)

    st.markdown("<h4 style='text-align:center; color:#38BDF8;'>📊 Financial Overview</h4>", unsafe_allow_html=True)
    
    # ডাটা লোড
    data = get_home_stats()

    # ফিনান্সিয়াল কার্ডস
    f1, f2 = st.columns(2)
    with f1:
        st.markdown(f'<div class="stat-card"><p class="stat-title">Total Savings</p><p class="stat-value" style="color:#38BDF8;">৳{data["savings"]:,.0f}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><p class="stat-title">Last FDR Month</p><p class="stat-value" style="color:#F59E0B;">{data["last_fdr"]}</p></div>', unsafe_allow_html=True)
    with f2:
        st.markdown(f'<div class="stat-card"><p class="stat-title">Total FDR Amount</p><p class="stat-value" style="color:#8B5CF6;">৳{data["fdr"]:,.0f}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><p class="stat-title">Total Late Fee</p><p class="stat-value" style="color:#EF4444;">৳{data["fine"]:,.0f}</p></div>', unsafe_allow_html=True)
