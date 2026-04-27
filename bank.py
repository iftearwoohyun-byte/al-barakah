import streamlit as st
import pandas as pd
from datetime import datetime
import database as db 

# --- ১. তারিখ প্রসেসিং ও সর্টিং লজিক ---
def get_sorted_fdr_list():
    conn = db.connect_db()
    if conn:
        try:
            ws = conn.worksheet("FDR_Data")
            data = ws.get_all_records()
            if not data: return []
            
            # ডাটাফ্রেম তৈরি করে তারিখ অনুযায়ী সাজানো (Sorting)
            df = pd.DataFrame(data)
            # তারিখ কলামকে আসল ডেট ফরম্যাটে রূপান্তর যাতে সিরিয়াল ঠিক থাকে
            df['temp_date'] = pd.to_datetime(df['Open_Date'], format='%m/%d/%y', errors='coerce')
            df = df.sort_values(by='temp_date', ascending=True) # ছোট থেকে বড় (সিরিয়াল)
            return df.to_dict('records')
        except Exception as e:
            return []
    return []

# --- ২. মাস ও সাল ফরম্যাট ---
def format_fdr_date(date_str):
    try:
        dt = datetime.strptime(str(date_str), '%m/%d/%y')
        return dt.strftime("%B"), dt.strftime("%Y")
    except:
        return "Unknown", ""

# --- ৩. মেইন শো ফাংশন (প্রিমিয়াম গ্রিড) ---
def show():
    user_role = st.session_state.get("role", "Member")
    
    # ডিজাইন স্টাইল (গ্লাস-মর্ফিজম ইফেক্ট)
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A; }
        .fdr-grid-card {
            background: rgba(30, 41, 59, 0.7);
            border-radius: 15px;
            padding: 20px;
            border-left: 5px solid #38BDF8;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-bottom: 15px;
            text-align: center;
        }
        .date-box { background: #1E293B; padding: 5px; border-radius: 8px; margin-bottom: 10px; }
        .month-name { color: #38BDF8; font-size: 1.2rem; font-weight: bold; margin: 0; }
        .year-name { color: #94A3B8; font-size: 0.9rem; margin: 0; }
        .amount-val { color: #FFFFFF; font-size: 1.5rem; font-weight: bold; margin: 10px 0; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;'>🏦 BANKING MANAGEMENT</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏠 OVERVIEW", "💰 FDR LEDGER", "🏦 SAVINGS"])

    # --- ওভারভিউ ট্যাব ---
    with tab1:
        fdr_list = get_sorted_fdr_list()
        fdr_total = sum(float(str(r['Amount']).replace(',', '')) for r in fdr_list) if fdr_list else 0
        
        # গুগল শিট থেকে সঞ্চয় ব্যালেন্স আনা
        conn = db.connect_db()
        try:
            ws_bal = conn.worksheet("Bank_Savings")
            savings_bal = float(ws_bal.cell(2, 1).value or 0)
        except: savings_bal = 0.0

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="fdr-grid-card"><p style="color:#94A3B8;margin:0;">SAVINGS</p><p class="amount-val">৳ {savings_bal:,.2f}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="fdr-grid-card" style="border-left-color:#8B5CF6;"><p style="color:#94A3B8;margin:0;">TOTAL FDR</p><p class="amount-val">৳ {fdr_total:,.2f}</p></div>', unsafe_allow_html=True)

    # --- FDR লেজার ট্যাব (সিরিয়াল গ্রিড) ---
    with tab2:
        col_title, col_btn = st.columns([3, 1])
        with col_title: st.write("### 📅 Monthly FDR Serial")
        with col_btn:
            if user_role == "Admin":
                from bank import open_add_fdr_form # ডায়ালগ ফাংশন
                if st.button("➕ NEW ENTRY"): open_add_fdr_form()

        sorted_data = get_sorted_fdr_list()
        
        if not sorted_data:
            st.info("গুগল শিটে কোনো FDR ডাটা পাওয়া যায়নি।")
        else:
            # ৩ কলামের গ্রিড
            cols = st.columns(3)
            for i, row in enumerate(sorted_data):
                month, year = format_fdr_date(row['Open_Date'])
                st_color = "#10B981" if row['Status'] == "Active" else "#F59E0B"
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="fdr-grid-card">
                            <div class="date-box">
                                <p class="month-name">{month}</p>
                                <p class="year-name">{year}</p>
                            </div>
                            <p class="amount-val">৳ {float(row['Amount']):,.0f}</p>
                            <p style="color:{st_color}; font-size:12px; font-weight:bold;">● {row['Status'].upper()}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # অ্যাকশন বাটন
                    b1, b2 = st.columns(2)
                    with b1:
                        if row['Link']: st.link_button("🌐 VIEW", row['Link'], use_container_width=True)
                    with b2:
                        if user_role == "Admin":
                            if st.button("🗑️", key=f"del_{row['ID']}", use_container_width=True):
                                # ডিলিট লজিক (গুগল শিট থেকে)
                                conn = db.connect_db()
                                ws = conn.worksheet("FDR_Data")
                                target = ws.find(str(row['ID']))
                                if target:
                                    ws.delete_rows(target.row)
                                    st.success("Deleted!")
                                    st.rerun()

    # --- সঞ্চয় ট্যাব ---
    with tab3:
        # ব্যালেন্স আপডেট লজিক (আগের মতোই)
        pass
