import streamlit as st
import pandas as pd
from datetime import datetime
import database as db 

def get_ledger_data():
    conn = db.connect_db()
    income_list = []
    expense_list = []
    
    if conn:
        try:
            # 1. Initial Entry: Form Fee (Fixed 10,000/-)
            income_list.append({
                "Date": "Initial",
                "Particulars": "Form Fee (20 Shares x 500)",
                "Amount": 10000.0
            })
            
            # 2. Member Savings (Handling Duplicate Header Error)
            try:
                ws_savings = conn.worksheet("Savings")
                s_values = ws_savings.get_all_values()
                if len(s_values) > 1:
                    df_s = pd.DataFrame(s_values[1:], columns=s_values[0])
                    exclude = ['ID', 'Name', 'Shares', 'Total', 'Remarks', 'Fine']
                    val_cols = [c for c in df_s.columns if c not in exclude and c.strip() != '']
                    
                    # Sum each member's total savings
                    for index, row in df_s.iterrows():
                        m_total = 0
                        for col in val_cols:
                            try:
                                m_total += float(str(row[col]).replace(',', ''))
                            except: pass
                        
                        if m_total > 0:
                            income_list.append({
                                "Date": "Ongoing",
                                "Particulars": f"Savings: {row.get('Name', 'Member')}",
                                "Amount": m_total
                            })
            except: pass

            # 3. Expenses from Google Sheets
            try:
                ws_expense = conn.worksheet("Expenses")
                ex_values = ws_expense.get_all_values()
                if len(ex_values) > 1:
                    df_ex = pd.DataFrame(ex_values[1:], columns=ex_values[0])
                    for index, row in df_ex.iterrows():
                        expense_list.append({
                            "Date": row.get('Date', 'N/A'),
                            "Particulars": row.get('Description', 'Expense'),
                            "Amount": float(str(row.get('Amount', 0)).replace(',', ''))
                        })
            except: pass
            
        except Exception as e:
            st.error(f"Data Load Error: {e}")
            
    return income_list, expense_list

@st.dialog("💸 Add New Expense")
def add_expense_form():
    st.write("### NEW EXPENSE ENTRY")
    e_date = st.date_input("Date", datetime.now())
    e_desc = st.text_input("Description (Details)")
    e_amount = st.number_input("Amount (BDT)", min_value=0.0)
    
    if st.button("SAVE RECORD", type="primary", use_container_width=True):
        if e_desc and e_amount > 0:
            conn = db.connect_db()
            ws = conn.worksheet("Expenses")
            ws.append_row([e_date.strftime('%Y-%m-%d'), e_desc, e_amount])
            st.success("Expense saved successfully!")
            st.rerun()

def show():
    # Advanced CSS for Professional UI
    st.markdown("""
        <style>
        .ledger-container {
            background: #1E293B;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #334155;
            margin-bottom: 20px;
        }
        .header-title { color: #38BDF8; font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .summary-table {
            width: 100%;
            border-collapse: collapse;
            background: #0F172A;
            border-radius: 8px;
            overflow: hidden;
            margin-top: 20px;
        }
        .summary-table th, .summary-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #334155;
            color: #F8FAFC;
        }
        .summary-table th { background: #334155; color: #38BDF8; }
        .total-box { font-size: 18px; font-weight: bold; text-align: right; padding-top: 10px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; color:#38BDF8;'>📒 Daily Cash Ledger</h1>", unsafe_allow_html=True)
    st.write("---")

    # Action Buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ ADD OTHER INCOME", use_container_width=True):
            st.toast("Feature coming soon!")
    with c2:
        if st.button("💸 RECORD EXPENSE", type="primary", use_container_width=True):
            add_expense_form()

    # Load Data
    inc_data, exp_data = get_ledger_data()
    df_inc = pd.DataFrame(inc_data)
    df_exp = pd.DataFrame(exp_data)

    # Side-by-Side View
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="ledger-container"><div class="header-title">📥 Income List</div>', unsafe_allow_html=True)
        if not df_inc.empty:
            st.dataframe(df_inc, use_container_width=True, hide_index=True)
            t_in = df_inc['Amount'].sum()
            st.markdown(f'<div class="total-box" style="color:#22C55E;">Total Income: ৳{t_in:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="ledger-container"><div class="header-title">📤 Expense List</div>', unsafe_allow_html=True)
        if not df_exp.empty:
            st.dataframe(df_exp, use_container_width=True, hide_index=True)
            t_out = df_exp['Amount'].sum()
            st.markdown(f'<div class="total-box" style="color:#EF4444;">Total Expense: ৳{t_out:,.0f}</div>', unsafe_allow_html=True)
        else: st.info("No expenses recorded yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Professional Balance Sheet Table ---
    st.write("---")
    st.markdown("<div class='header-title'>💰 Cash Position Summary</div>", unsafe_allow_html=True)
    
    total_in = df_inc['Amount'].sum() if not df_inc.empty else 0
    total_out = df_exp['Amount'].sum() if not df_exp.empty else 0
    net_bal = total_in - total_out

    st.markdown(f"""
        <table class="summary-table">
            <thead>
                <tr>
                    <th>Description</th>
                    <th style="text-align:right;">Amount (BDT)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Total Income (Savings + Fees)</td>
                    <td style="text-align:right; color:#22C55E;">৳ {total_in:,.2f}</td>
                </tr>
                <tr>
                    <td>Total Office Expenses</td>
                    <td style="text-align:right; color:#EF4444;">৳ {total_out:,.2f}</td>
                </tr>
                <tr style="background: #1E293B;">
                    <td style="font-weight:bold; color:#38BDF8;">Net Cash in Hand</td>
                    <td style="text-align:right; font-weight:bold; color:#38BDF8; font-size: 1.2em;">৳ {net_bal:,.2f}</td>
                </tr>
            </tbody>
        </table>
    """, unsafe_allow_html=True)
