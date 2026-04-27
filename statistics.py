import streamlit as st
import pandas as pd
import plotly.express as px
import database as db 

def show():
    st.markdown("<h1 style='text-align:center; color:#38BDF8;'>📈 Business Statistics & Analytics</h1>", unsafe_allow_html=True)
    st.write("---")

    # --- ১. ডাটা সংগ্রহ (গুগল শিট থেকে) ---
    conn = db.connect_db()
    total_savings = 0
    total_fdr = 0
    bank_balance = 0

    if conn:
        try:
            # ক. মেম্বার সেভিংস (Savings শিট থেকে) - ডুপ্লিকেট হেডার এরর ফিক্সসহ
            ws_savings = conn.worksheet("Savings")
            all_data = ws_savings.get_all_values()
            if len(all_data) > 1:
                # pandas দিয়ে ডাটা পড়া যাতে ডুপ্লিকেট কলামে সমস্যা না হয়
                df_s = pd.DataFrame(all_data[1:], columns=all_data[0])
                # ID, Name, Shares বাদ দিয়ে বাকি সব কলামের যোগফল
                cols_to_sum = [c for c in df_s.columns if c not in ['ID', 'Name', 'Shares'] and c.strip() != '']
                for col in cols_to_sum:
                    total_savings += pd.to_numeric(df_s[col].str.replace(',', ''), errors='coerce').sum()

            # খ. FDR ইনভেস্টমেন্ট (FDR_Data শিট থেকে)
            ws_fdr = conn.worksheet("FDR_Data")
            fdr_data = ws_fdr.get_all_values()
            if len(fdr_data) > 1:
                df_f = pd.DataFrame(fdr_data[1:], columns=fdr_data[0])
                total_fdr = pd.to_numeric(df_f['Amount'].str.replace(',', ''), errors='coerce').sum()

            # গ. ব্যাংক ব্যালেন্স (Bank_Savings শিট থেকে)
            ws_bank = conn.worksheet("Bank_Savings")
            bank_val = ws_bank.cell(2, 1).value
            bank_balance = float(bank_val) if bank_val else 0.0

        except Exception as e:
            st.error(f"ডাটা লোড এরর: {e}")

    # --- ২. চার্ট প্রদর্শন ---
    total_all = total_savings + total_fdr + bank_balance

    if total_all > 0:
        chart_df = pd.DataFrame({
            "Category": ["Member Savings", "FDR Investment", "Bank Cash"],
            "Amount": [total_savings, total_fdr, bank_balance]
        })

        fig = px.pie(chart_df, values='Amount', names='Category', hole=0.5,
                     color_discrete_sequence=['#38BDF8', '#8B5CF6', '#F59E0B'],
                     template="plotly_dark")
        
        st.plotly_chart(fig, use_container_width=True)

        # --- ৩. স্ট্যাটাস কার্ডস ---
        st.markdown("""
            <style>
            .stat-box { background: #1E293B; padding: 20px; border-radius: 15px; border-bottom: 4px solid #38BDF8; text-align: center; }
            .stat-v { color: white; font-size: 22px; font-weight: bold; }
            .stat-l { color: #94A3B8; font-size: 13px; }
            </style>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-l">মোট সঞ্চয়</div><div class="stat-v">৳{total_savings:,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box" style="border-bottom-color:#8B5CF6;"><div class="stat-l">মোট FDR</div><div class="stat-v">৳{total_fdr:,.0f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-box" style="border-bottom-color:#F59E0B;"><div class="stat-l">ব্যাংক ক্যাশ</div><div class="stat-v">৳{bank_balance:,.0f}</div></div>', unsafe_allow_html=True)
    else:
        st.info("গুগল শিটে কোনো ডাটা পাওয়া যায়নি।")
