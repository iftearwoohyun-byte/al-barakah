import streamlit as st
import pandas as pd
import database as db 

def load_all_savings():
    conn = db.connect_db()
    if conn:
        try:
            worksheet = conn.worksheet("Savings")
            all_values = worksheet.get_all_values()
            if len(all_values) > 1:
                headers = all_values[0]
                data = all_values[1:]
                df = pd.DataFrame(data, columns=headers)
                return df.to_dict('records'), worksheet
            return [], worksheet
        except Exception as e:
            st.error(f"Error loading worksheet: {e}")
            return [], None
    return [], None

@st.dialog("Collect Savings & Late Fee")
def add_deposit():
    st.markdown("<h3 style='color:#1A365D;'>নতুন সঞ্চয় ও জরিমানা জমা</h3>", unsafe_allow_html=True)
    members_data = db.get_live_data() 
    
    if not members_data:
        st.error("মেম্বার লিস্ট পাওয়া যায়নি!")
        return

    names = [f"{m['Name']} (ID: {m['ID']})" for m in members_data]
    selected_member = st.selectbox("মেম্বার সিলেক্ট করুন", names)
    
    # Nov-25 থেকে Oct-27 পর্যন্ত সব মাস
    months = [
        "Nov_25", "Dec_25", "Jan_26", "Feb_26", "Mar_26", "Apr_26", "May_26", "Jun_26", "Jul_26", "Aug_26", "Sep_26", "Oct_26",
        "Nov_26", "Dec_26", "Jan_27", "Feb_27", "Mar_27", "Apr_27", "May_27", "Jun_27", "Jul_27", "Aug_27", "Sep_27", "Oct_27"
    ]
    selected_month = st.selectbox("কোন মাসের টাকা?", months)
    
    m_id = selected_member.split("(ID: ")[1].replace(")", "")
    member_name = selected_member.split(" (ID:")[0]
    
    member = next((m for m in members_data if str(m['ID']) == str(m_id)), None)
    share_count = int(member.get('Share', member.get('Shares', 1))) if member else 1
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("সঞ্চয় জমা (টাকা)", value=share_count * 5000)
    with col2:
        fine = st.number_input("জরিমানা / Late Fee (টাকা)", value=0)

    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        conn = db.connect_db()
        if conn:
            try:
                ws_sav = conn.worksheet("Savings")
                headers = ws_sav.row_values(1)
                
                # --- অটো কলাম তৈরি করার লজিক ---
                if selected_month not in headers:
                    # নতুন কলামটি শিটের একদম শেষে যোগ হবে
                    new_col_idx = len(headers) + 1
                    ws_sav.update_cell(1, new_col_idx, selected_month)
                    headers.append(selected_month) # আপডেট হেডার লিস্ট
                    st.toast(f"নতুন কলাম '{selected_month}' তৈরি করা হয়েছে।")

                col_idx = headers.index(selected_month) + 1
                all_ids = [str(x) for x in ws_sav.col_values(1)]
                
                if str(m_id) in all_ids:
                    row_idx = all_ids.index(str(m_id)) + 1
                    ws_sav.update_cell(row_idx, col_idx, amount)
                    
                    # জরিমানা থাকলে 'Late Fee' শিটে জমা হবে
                    if fine > 0:
                        try:
                            ws_fine = conn.worksheet("Late Fee")
                            ws_fine.append_row([member_name, selected_month, fine])
                        except:
                            st.warning("Late Fee শিটটি পাওয়া যায়নি!")
                            
                    st.success(f"{member_name}-এর {selected_month} মাসের সঞ্চয় জমা হয়েছে।")
                    st.rerun()
                else:
                    st.error("মেম্বার আইডি খুঁজে পাওয়া যায়নি!")
            except Exception as e:
                st.error(f"Save Error: {e}")

def show():
    st.markdown("""
        <style>
        .savings-header { background-color: #1A365D; padding: 40px; text-align: center; border-radius: 15px; margin-bottom: 25px; }
        .header-text { color: white !important; font-size: 32px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="savings-header"><h1 class="header-text">AL-BARAKAH SAVINGS LEDGER</h1></div>', unsafe_allow_html=True)

    if st.button("➕ ADD SAVINGS & FINE"):
        add_deposit()
    
    st.markdown("<br>", unsafe_allow_html=True)

    savings_list, _ = load_all_savings()
    
    if savings_list:
        all_months = [
            "Nov_25", "Dec_25", "Jan_26", "Feb_26", "Mar_26", "Apr_26", "May_26", "Jun_26", "Jul_26", "Aug_26", "Sep_26", "Oct_26",
            "Nov_26", "Dec_26", "Jan_27", "Feb_27", "Mar_27", "Apr_27", "May_27", "Jun_27", "Jul_27", "Aug_27", "Sep_27", "Oct_27"
        ]
        
        table_rows = []
        for row in savings_list:
            total_bal = 0
            last_m = "No Data"
            
            for m in all_months:
                val = row.get(m, 0)
                if val and str(val).strip() != "":
                    try:
                        num_val = float(val)
                        total_bal += num_val
                        last_m = m.replace("_", " ")
                    except: pass
            
            table_rows.append({
                "ID": row.get('ID', ''),
                "Member Name": row.get('Name', ''),
                "Shares": row.get('Shares', row.get('Share', 0)),
                "Last Paid": last_m,
                "Total Savings": f"{total_bal:,.2f}"
            })
            
        st.table(pd.DataFrame(table_rows))
    else:
        st.info("গুগল শিটে কোনো ডাটা নেই।")
