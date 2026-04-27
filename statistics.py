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
            # ১. জরিমানা ক্যালকুলেশন (সরাসরি 'Late Fee' শিট থেকে)
            try:
                ws_late_fee = conn.worksheet("Late Fee")
                # শিটের সব ডাটা নিয়ে আসা
                fine_data = ws_late_fee.get_all_values()
                
                for row in fine_data:
                    for val in row:
                        try:
                            # কমা সরিয়ে সংখ্যায় রূপান্তর এবং যোগ করা
                            clean_val = str(val).replace(',', '').strip()
                            if clean_val:
                                total_fine += float(clean_val)
                        except ValueError:
                            continue # টেক্সট থাকলে তা এড়িয়ে যাবে
            except:
                st.warning("'Late Fee' শিটটি খুঁজে পাওয়া যায়নি!")

            # ২. মূল সঞ্চয় (Savings শিট থেকে)
            ws_savings = conn.worksheet("Savings")
            s_data = ws_savings.get_all_values()
            if len(s_data) > 1:
                df_s = pd.DataFrame(s_data[1:], columns=s_data[0])
                # ID, Name, Shares বাদ দিয়ে বাকি মাসের কলামগুলোর যোগফল
                exclude = ['ID', 'Name', 'Shares', 'Total', 'Remarks', 'Fine'] 
                val_cols = [c for c in df_s.columns if c not in exclude and c.strip() != '']
                for col in val_cols:
                    total_savings += pd.to_numeric(df_s[col].str.replace(',', ''), errors='coerce').sum()

            # ৩. FDR ও ব্যাংক ব্যালেন্স
            try:
                ws_fdr = conn.worksheet("FDR_Data")
                fdr_df = pd.DataFrame(ws_fdr.get_all_records())
                total_fdr = pd.to_numeric(fdr_df['Amount'].astype(str).str.replace(',', ''), errors='coerce').sum()
            except: pass

            try:
                ws_bank = conn.worksheet("Bank_Savings")
                bank_balance = float(ws_bank.cell(2, 1).value or 0)
            except: pass

        except Exception as e:
            st.error(f"ডাটা লোড এরর: {e}")

    # --- ৪. ভিজ্যুয়ালাইজেশন ---
    if (total_savings + total_fine + total_fdr + bank_balance) > 0:
        chart_df = pd.DataFrame({
            "বিভাগ": ["মূল সঞ্চয়", "মোট জরিমানা", "FDR ইনভেস্টমেন্ট", "ব্যাংক ক্যাশ"],
            "পরিমাণ": [total_savings, total_fine, total_fdr, bank_balance]
        })

        fig = px.pie(chart_df, values='পরিমাণ', names='বিভাগ', hole=0.5,
                     color_discrete_sequence=['#22C55E', '#EF4444', '#8B5CF6', '#38BDF8'],
                     template="plotly_dark")
        
        st.plotly_chart(fig, use_container_width=True)

        # --- ৫. ইনফো কার্ডস ---
        st.markdown("""
            <style>
            .stat-card { background: #1E293B; padding: 15px; border-radius: 12px; border-bottom: 4px solid #38BDF8; text-align: center; margin-bottom: 15px; }
            .v-num { color: white; font-size: 20px; font-weight: bold; margin: 0; }
            .v-lab { color: #94A3B8; font-size: 11px; margin: 0; }
            </style>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="stat-card" style="border-bottom-color:#22C55E;"><p class="v-lab">মোট মূল সঞ্চয়</p><p class="v-num">৳{total_savings:,.0f}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card" style="border-bottom-color:#EF4444;"><p class="v-lab">মোট জরিমানা (Late Fee)</p><p class="v-num">৳{total_fine:,.0f}</p></div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown(f'<div class="stat-card" style="border-bottom-color:#8B5CF6;"><p class="v-lab">মোট FDR</p><p class="v-num">৳{total_fdr:,.0f}</p></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card" style="border-bottom-color:#38BDF8;"><p class="v-lab">ব্যাংক ব্যালেন্স</p><p class="v-num">৳{bank_balance:,.2f}</p></div>', unsafe_allow_html=True)
    else:
        st.warning("কোনো ডাটা পাওয়া যায়নি। অনুগ্রহ করে গুগল শিট চেক করুন।")
