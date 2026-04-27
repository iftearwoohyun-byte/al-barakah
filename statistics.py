import streamlit as st
import pandas as pd
import plotly.express as px
import database as db 

def show():
    st.markdown("<h1 style='text-align:center; color:#38BDF8;'>📊 Business Analytics</h1>", unsafe_allow_html=True)
    st.write("---")

    conn = db.connect_db()
    total_savings = 0
    total_fine = 0
    total_fdr = 0
    bank_balance = 0

    if conn:
        try:
            # ১. সঞ্চয় ও জরিমানা (Savings শিট থেকে)
            ws_savings = conn.worksheet("Savings")
            all_data = ws_savings.get_all_values()
            if len(all_data) > 1:
                df_s = pd.DataFrame(all_data[1:], columns=all_data[0])
                
                # জরিমানা কলাম আলাদা করা (আপনার শিটে 'Fine' নামে কলাম আছে ধরে নিচ্ছি)
                if 'Fine' in df_s.columns:
                    total_fine = pd.to_numeric(df_s['Fine'].str.replace(',', ''), errors='coerce').sum()
                
                # জমা ক্যালকুলেশন (ID, Name, Shares, Fine বাদে বাকি সব)
                exclude = ['ID', 'Name', 'Shares', 'Fine', 'Total', 'Remarks']
                val_cols = [c for c in df_s.columns if c not in exclude and c.strip() != '']
                
                for col in val_cols:
                    total_savings += pd.to_numeric(df_s[col].str.replace(',', ''), errors='coerce').sum()

            # ২. FDR ও ব্যাংক ব্যালেন্স
            ws_fdr = conn.worksheet("FDR_Data")
            fdr_vals = ws_fdr.get_all_values()
            if len(fdr_vals) > 1:
                df_f = pd.DataFrame(fdr_vals[1:], columns=fdr_vals[0])
                total_fdr = pd.to_numeric(df_f['Amount'].str.replace(',', ''), errors='coerce').sum()

            ws_bank = conn.worksheet("Bank_Savings")
            bank_balance = float(ws_bank.cell(2, 1).value or 0)

        except Exception as e:
            st.error(f"ডাটা প্রসেসিং এরর: {e}")

    # --- ৩. ভিজ্যুয়ালাইজেশন ---
    if (total_savings + total_fine + total_fdr + bank_balance) > 0:
        # চার্ট ডাটা
        chart_df = pd.DataFrame({
            "বিভাগ": ["মূল সঞ্চয়", "মোট জরিমানা", "FDR ইনভেস্টমেন্ট", "ব্যাংক ক্যাশ"],
            "পরিমাণ": [total_savings, total_fine, total_fdr, bank_balance]
        })

        fig = px.pie(chart_df, values='পরিমাণ', names='বিভাগ', hole=0.5,
                     color_discrete_sequence=['#22C55E', '#EF4444', '#8B5CF6', '#38BDF8'],
                     template="plotly_dark")
        
        st.plotly_chart(fig, use_container_width=True)

        # --- ৪. তথ্য কার্ডসমূহ ---
        st.markdown("""
            <style>
            .stat-card { background: #1E293B; padding: 15px; border-radius: 12px; border-bottom: 4px solid #38BDF8; text-align: center; }
            .v-num { color: white; font-size: 20px; font-weight: bold; margin: 0; }
            .v-lab { color: #94A3B8; font-size: 11px; margin: 0; }
            </style>
        """, unsafe_allow_html=True)

        # প্রথম সারি: সঞ্চয় ও জরিমানা
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="stat-card" style="border-bottom-color:#22C55E;"><p class="v-lab">মোট জমা (Savings)</p><p class="v-num">৳{total_savings:,.0f}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card" style="border-bottom-color:#EF4444;"><p class="v-lab">মোট জরিমানা (Fine)</p><p class="v-num">৳{total_fine:,.0f}</p></div>', unsafe_allow_html=True)

        # দ্বিতীয় সারি: FDR ও ব্যাংক
        st.write("")
        c3, c4 = st.columns(2)
        with c3:
            st.markdown(f'<div class="stat-card" style="border-bottom-color:#8B5CF6;"><p class="v-lab">মোট FDR</p><p class="v-num">৳{total_fdr:,.0f}</p></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card" style="border-bottom-color:#38BDF8;"><p class="v-lab">ব্যাংক ব্যালেন্স</p><p class="v-num">৳{bank_balance:,.2f}</p></div>', unsafe_allow_html=True)
    else:
        st.warning("বিশ্লেষণ করার মতো পর্যাপ্ত ডাটা পাওয়া যায়নি।")
