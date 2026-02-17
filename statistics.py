import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import json
import os
from streamlit_option_menu import option_menu

def show():
    st.header("📈 Business Statistics & Analytics")
    st.write("---")

    # --- ডাটা সংগ্রহ ---
    total_savings = 0
    # ১. JSON ফাইল (savings_data.json) থেকে ডাটা
    if os.path.exists("savings_data.json"):
        with open("savings_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for s in data:
                # 'ID', 'Name', 'Shares' বাদে বাকি মাসগুলোর যোগফল
                for k, v in s.items():
                    if k not in ['ID', 'Name', 'Shares'] and v != '':
                        try:
                            total_savings += float(str(v).replace(",", ""))
                        except: pass

    # ২. SQLite ডাটাবেজ (somiti_ultimate_v5.db) থেকে ডাটা
    total_fdr = 0
    bank_balance = 0
    if os.path.exists("somiti_ultimate_v5.db"):
        conn = sqlite3.connect("somiti_ultimate_v5.db")
        try:
            # FDR ডাটা
            fdr_df = pd.read_sql("SELECT amount FROM fdr_data", conn)
            total_fdr = fdr_df['amount'].sum()
            # ব্যাংক ব্যালেন্স
            bank_balance = pd.read_sql("SELECT balance FROM savings_data", conn).iloc[0,0]
        except: pass
        finally: conn.close()

    # --- পাই চার্ট প্রদর্শন ---
    if (total_savings + total_fdr + bank_balance) > 0:
        chart_data = pd.DataFrame({
            "বিভাগ": ["মেম্বার সেভিংস", "FDR ইনভেস্টমেন্ট", "ব্যাংক ব্যালেন্স"],
            "পরিমাণ": [total_savings, total_fdr, bank_balance]
        })

        # ডোনাট স্টাইল পাই চার্ট
        fig = px.pie(chart_data, values='পরিমাণ', names='বিভাগ', hole=0.5,
                     color_discrete_sequence=px.colors.sequential.RdBu)
        
        st.plotly_chart(fig, use_container_width=True)

        # --- স্ট্যাটাস কার্ডস ---
        c1, c2, c3 = st.columns(3)
        c1.metric("মোট সেভিংস", f"৳{total_savings:,.0f}")
        c2.metric("মোট FDR", f"৳{total_fdr:,.0f}")
        c3.metric("ব্যাংক ক্যাশ", f"৳{bank_balance:,.0f}")
    else:
        st.warning("বিশ্লেষণ করার মতো পর্যাপ্ত ডাটা খুঁজে পাওয়া যায়নি।")
