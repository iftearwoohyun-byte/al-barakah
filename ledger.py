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
            income_list.append({"Date": "Initial", "Particulars": "Form Fee (20 Shares x 500)", "Amount": 10000.0})
            
            # 2. Total Late Fee (From 'Late Fee' Sheet)
            try:
                ws_late = conn.worksheet("Late Fee")
                late_vals = ws_late.get_all_values()
                total_late = sum(float(str(v).replace(',', '')) for r in late_vals for v in r if str(v).replace('.', '').isdigit())
                if total_late > 0:
                    income_list.append({"Date": "Ongoing", "Particulars": "Total Late Fee Collection", "Amount": total_late})
            except: pass

            # 3. Member Savings
            ws_s = conn.worksheet("Savings")
            s_vals = ws_s.get_all_values()
            if len(s_vals) > 1:
                df_s = pd.DataFrame(s_vals[1:], columns=s_vals[0])
                exclude = ['ID', 'Name', 'Shares', 'Total', 'Remarks', 'Fine']
                val_cols = [c for c in df_s.columns if c in df_s.columns and c.strip() != '' and c not in exclude]
                for _, row in df_s.iterrows():
                    m_total = sum(float(str(row[c]).replace(',', '')) for c in val_cols if str(row[c]).replace('.', '').isdigit())
                    if m_total > 0:
                        income_list.append({"Date": "Ongoing", "Particulars": f"Savings: {row['Name']}", "Amount": m_total})

            # 4. Expense List (With Row ID for Editing)
            ws_e = conn.worksheet("Expenses")
            ex_vals = ws_e.get_all_values()
            if len(ex_vals) > 1:
                df_ex = pd.DataFrame(ex_vals[1:], columns=ex_vals[0])
                for index, row in df_ex.iterrows():
                    expense_list.append({
                        "Row": index + 2,
                        "Date": row.get('Date', 'N/A'),
                        "Particulars": row.get('Description', 'Expense'),
                        "Amount": float(str(row.get('Amount', 0)).replace(',', ''))
                    })
        except: pass
    return income_list, expense_list

@st.dialog("📝 Edit Expense")
def edit_expense_form(row_index, current_date, current_desc, current_amount):
    u_date = st.date_input("Update Date", datetime.now())
    u_desc = st.text_input("Update Description", value=current_desc)
    u_amount = st.number_input("Update Amount", value=float(current_amount))
    if st.button("UPDATE NOW", type="primary", use_container_width=True):
        conn = db.connect_db()
        ws = conn.worksheet("Expenses")
        ws.update(f"A{row_index}:C{row_index}", [[u_date.strftime('%Y-%m-%d'), u_desc, u_amount]])
        st.success("Record Updated!")
        st.rerun()

def show():
    user_role = st.session_state.get("role", "Member")
    st.markdown("<h1 style='text-align:center; color:#38BDF8;'>📒 Daily Cash Ledger</h1>", unsafe_allow_html=True)

    # Action Buttons (Admin Only)
    if user_role == "Admin":
        c_btn1, c_btn2 = st.columns(2)
        with c_btn2:
            if st.button("💸 RECORD NEW EXPENSE", type="primary", use_container_width=True):
                # add_expense_form code... (Previous Dialog)
                pass

    inc_data, exp_data = get_ledger_data()
    col_l, col_r = st.columns(2)

    # Income Side
    with col_l:
        st.markdown("### 📥 Income List")
        st.dataframe(pd.DataFrame(inc_data), use_container_width=True, hide_index=True)
        t_in = sum(d['Amount'] for d in inc_data)
        st.markdown(f"<h4 style='text-align:right; color:#22C55E;'>Total Income: ৳{t_in:,.0f}</h4>", unsafe_allow_html=True)

    # Expense Side with Edit Option
    with col_r:
        st.markdown("### 📤 Expense List")
        if exp_data:
            for i, item in enumerate(exp_data):
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"**{item['Particulars']}**")
                    c1.caption(f"Date: {item['Date']} | Amount: ৳{item['Amount']:,.0f}")
                    if user_role == "Admin":
                        if c2.button("Edit", key=f"ex_{i}"):
                            edit_expense_form(item['Row'], item['Date'], item['Particulars'], item['Amount'])
        else:
            st.info("No expenses found.")

    # Cash Summary Table
    t_out = sum(d['Amount'] for d in exp_data)
    st.write("---")
    st.markdown(f"""
        <div style="background:#1E293B; padding:20px; border-radius:12px; border:1px solid #334155; text-align:center;">
            <h2 style="margin:0; color:#38BDF8;">Cash in Hand: ৳ {(t_in - t_out):,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)
