import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime

# --- ডাটাবেস সেটআপ (খরচ সেভ করার জন্য) ---
def init_db():
    conn = sqlite3.connect("somiti_ultimate_v5.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            category TEXT,
            amount REAL
        )
    """)
    conn.commit()
    conn.close()

def show():
    st.header("📒 Daily Cash Ledger")
    init_db()

    # --- ১. নতুন লেনদেন (Expense) যোগ করার সেকশন ---
    with st.expander("➕ ADD NEW TRANSACTION (EXPENSE)"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ex_date = st.date_input("Date", datetime.now()).strftime("%Y-%m-%d")
        with col2:
            ex_cat = st.selectbox("Category", ["Office Stationery", "Rent", "Salary", "Electricity", "Others"])
        with col3:
            ex_amount = st.number_input("Amount", min_value=0.0, step=100.0)
        
        ex_desc = st.text_input("Description (e.g., Office Paper purchase)")
        
        if st.button("Save Transaction"):
            if ex_amount > 0 and ex_desc != "":
                conn = sqlite3.connect("somiti_ultimate_v5.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO expenses (date, description, category, amount) VALUES (?, ?, ?, ?)",
                               (ex_date, ex_desc, ex_cat, ex_amount))
                conn.commit()
                conn.close()
                st.success("Expense recorded successfully!")
                st.rerun()
            else:
                st.warning("Please enter amount and description.")

    # --- ২. ডাটা সংগ্রহ (Income & Expense) ---
    all_data = []

    # (ক) Income: Member Savings (JSON ফাইল থেকে আনা)
    if os.path.exists("savings_data.json"):
        with open("savings_data.json", "r", encoding="utf-8") as f:
            savings = json.load(f)
            for s in savings:
                member_total = 0
                for k, v in s.items():
                    if k not in ['ID', 'Name', 'Shares'] and v != '':
                        try:
                            val = float(str(v).replace(",", ""))
                            member_total += val
                        except: pass
                
                if member_total > 0:
                    all_data.append({
                        "Date": "Multiple", # বা নির্দিষ্ট তারিখ দিতে পারেন
                        "Description": f"Savings from {s['Name']} (ID: {s['ID']})",
                        "Category": "Income (Savings)",
                        "Debit (+)": member_total,
                        "Credit (-)": 0.0
                    })

    # (খ) Expense: ডাটাবেস থেকে খরচ আনা
    conn = sqlite3.connect("somiti_ultimate_v5.db")
    expenses_df = pd.read_sql("SELECT date, description, category, amount FROM expenses", conn)
    conn.close()

    for index, row in expenses_df.iterrows():
        all_data.append({
            "Date": row['date'],
            "Description": row['description'],
            "Category": row['category'],
            "Debit (+)": 0.0,
            "Credit (-)": row['amount']
        })

    # --- ৩. টেবিল তৈরি এবং ব্যালেন্স ক্যালকুলেশন ---
    if all_data:
        df = pd.DataFrame(all_data)
        
        # ব্যালেন্স কলাম তৈরি
        df['Balance'] = df['Debit (+)'] - df['Credit (-)']
        # ক্রমপুঞ্জিত যোগফল (Cumulative Sum) দিয়ে রানিং ব্যালেন্স বের করা
        df['Balance'] = df['Balance'].cumsum()

        # সুন্দর ফরমেটে দেখানো
        st.subheader("Transaction History")
        st.dataframe(df.style.format({
            "Debit (+)": "{:,.2f}",
            "Credit (-)": "{:,.2f}",
            "Balance": "{:,.2f}"
        }), use_container_width=True, hide_index=True)

        # ৪. সামারি কার্ডস
        st.write("---")
        c1, c2, c3 = st.columns(3)
        total_in = df['Debit (+)'].sum()
        total_out = df['Credit (-)'].sum()
        c1.metric("Total Income", f"৳{total_in:,.2f}")
        c2.metric("Total Expense", f"৳{total_out:,.2f}")
        c3.metric("Net Cash in Hand", f"৳{(total_in - total_out):,.2f}", delta_color="normal")

    else:
        st.info("No transactions found. Add an expense or check savings data.")

# CSS দিয়ে টেবিল এবং ফন্ট স্টাইল ঠিক করা
st.markdown("""
    <style>
    [data-testid="stHeader"] {background-color: rgba(0,0,0,0);}
    .stDataFrame {border: 1px solid #2d3e4b; border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)
