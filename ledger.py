import streamlit as st
import pandas as pd
from datetime import datetime
import database as db 

# --- ১. ডাটাবেজ ফাংশন (খরচ ও জমা) ---
def get_ledger_data():
    conn = db.connect_db()
    income_list = []
    expense_list = []
    
    if conn:
        try:
            # (ক) জমা: ফরম ফি (ফিক্সড ১০,০০০/-)
            income_list.append({
                "তারিখ": "প্রারম্ভিক",
                "খাত": "ফরম ফি (২০ শেয়ার x ৫০০)",
                "পরিমাণ": 10000.0
            })
            
            # (খ) জমা: মেম্বার সেভিংস (Savings শিট থেকে)
            ws_savings = conn.worksheet("Savings")
            savings_data = ws_savings.get_all_records()
            for row in savings_data:
                member_total = 0
                for k, v in row.items():
                    if k not in ['ID', 'Name', 'Shares', 'Total', 'Remarks']:
                        try:
                            val = float(str(v).replace(",", ""))
                            member_total += val
                        except: pass
                
                if member_total > 0:
                    income_list.append({
                        "তারিখ": "চলমান",
                        "খাত": f"সঞ্চয়: {row['Name']}",
                        "পরিমাণ": member_total
                    })

            # (গ) খরচ: Expense শিট থেকে (যদি থাকে)
            try:
                ws_expense = conn.worksheet("Expenses")
                expenses = ws_expense.get_all_records()
                for ex in expenses:
                    expense_list.append({
                        "তারিখ": ex.get('Date', 'N/A'),
                        "খাত": ex.get('Description', 'খরচ'),
                        "পরিমাণ": float(str(ex.get('Amount', 0)).replace(',', ''))
                    })
            except: pass
            
        except Exception as e:
            st.error(f"ডাটা লোড এরর: {e}")
            
    return income_list, expense_list

# --- ২. খরচ যোগ করার ফরম ---
@st.dialog("💸 নতুন খরচ যোগ করুন")
def add_expense_form():
    st.write("### EXPENSE ENTRY")
    e_date = st.date_input("তারিখ", datetime.now())
    e_desc = st.text_input("খরচের খাত (বিস্তারিত)")
    e_amount = st.number_input("টাকার পরিমাণ", min_value=0.0)
    
    if st.button("সেভ করুন", type="primary", use_container_width=True):
        if e_desc and e_amount > 0:
            conn = db.connect_db()
            ws = conn.worksheet("Expenses")
            ws.append_row([e_date.strftime('%Y-%m-%d'), e_desc, e_amount])
            st.success("খরচ সফলভাবে যোগ হয়েছে!")
            st.rerun()

def show():
    # লাক্সারি ডিজাইন CSS
    st.markdown("""
        <style>
        .ledger-box {
            background: #1E293B;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #334155;
            height: 100%;
        }
        .header-text { color: #38BDF8; font-size: 20px; font-weight: bold; margin-bottom: 15px; text-align: center; }
        .balance-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: #0F172A;
            border-radius: 10px;
            overflow: hidden;
        }
        .balance-table th, .balance-table td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #334155;
        }
        .balance-table th { background: #38BDF8; color: black; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; color:#38BDF8;'>📒 Daily Cash Ledger</h1>", unsafe_allow_html=True)
    st.write("---")

    # বাটন সেকশন
    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        if st.button("➕ অন্যান্য জমা যোগ করুন", use_container_width=True):
            st.info("এই ফিচারটি শীঘ্রই আসবে!")
    with c_btn2:
        if st.button("💸 খরচ যোগ করুন", type="primary", use_container_width=True):
            add_expense_form()

    # ডাটা সংগ্রহ
    income_data, expense_data = get_ledger_data()
    df_income = pd.DataFrame(income_data)
    df_expense = pd.DataFrame(expense_data)

    # পাশাপাশি দুই কলাম
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="ledger-box"><div class="header-text">📥 জমার লিস্ট (Income)</div>', unsafe_allow_html=True)
        if not df_income.empty:
            st.dataframe(df_income, use_container_width=True, hide_index=True)
            total_in = df_income['পরিমাণ'].sum()
            st.markdown(f"<h3 style='text-align:right; color:#22C55E;'>মোট জমা: ৳{total_in:,.0f}</h3>", unsafe_allow_html=True)
        else: st.write("কোনো জমার তথ্য নেই")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="ledger-box"><div class="header-text">📤 খরচের লিস্ট (Expense)</div>', unsafe_allow_html=True)
        if not df_expense.empty:
            st.dataframe(df_expense, use_container_width=True, hide_index=True)
            total_out = df_expense['পরিমাণ'].sum()
            st.markdown(f"<h3 style='text-align:right; color:#EF4444;'>মোট খরচ: ৳{total_out:,.0f}</h3>", unsafe_allow_html=True)
        else: st.info("এখনো কোনো খরচ রেকর্ড করা হয়নি")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ৩. বর্তমান ব্যালেন্স টেবিল ---
    st.write("---")
    st.markdown("<div class='header-text'>💰 বর্তমান স্থিতির হিসাব</div>", unsafe_allow_html=True)
    
    total_in = df_income['পরিমাণ'].sum() if not df_income.empty else 0
    total_out = df_expense['পরিমাণ'].sum() if not df_expense.empty else 0
    net_balance = total_in - total_out

    st.markdown(f"""
        <table class="balance-table">
            <tr>
                <th>বিবরণ</th>
                <th>টাকার পরিমাণ</th>
            </tr>
            <tr>
                <td>মোট সংগৃহীত ফান্ড (Income)</td>
                <td style="color:#22C55E;">৳ {total_in:,.2f}</td>
            </tr>
            <tr>
                <td>মোট খরচ (Expense)</td>
                <td style="color:#EF4444;">৳ {total_out:,.2f}</td>
            </tr>
            <tr style="background: #1E293B; font-weight: bold;">
                <td style="color: #38BDF8;">অবশিষ্ট ক্যাশ ব্যালেন্স (Net Cash)</td>
                <td style="color: #38BDF8; font-size: 1.2em;">৳ {net_balance:,.2f}</td>
            </tr>
        </table>
    """, unsafe_allow_html=True)
