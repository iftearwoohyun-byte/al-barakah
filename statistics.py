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
            # ক. মেম্বার সেভিংস ক্যালকুলেশন (Savings শিট থেকে)
            # আপনার মেম্বার লেজার স্ক্রিনশট অনুযায়ী সব মাসের জমা যোগ করা হচ্ছে
            ws_savings = conn.worksheet("Savings")
            savings_data = ws_savings.get_all_records()
            for row in savings_data:
                for col_name, val in row.items():
                    if col_name not in ['ID', 'Name', 'Shares']:
                        try:
                            # কমা সরিয়ে সংখ্যায় রূপান্তর
                            num = float(str(val).replace(",", ""))
                            total_savings += num
                        except: pass

            # খ. FDR ইনভেস্টমেন্ট (FDR_Data শিট থেকে)
            ws_fdr = conn.worksheet("FDR_Data")
            fdr_df = pd.DataFrame(ws_fdr.get_all_records())
            if not fdr_df.empty:
                total_fdr = pd.to_numeric(fdr_df['Amount'], errors='coerce').sum()

            # গ. ব্যাংক ব্যালেন্স (Bank_Savings শিট থেকে)
            ws_bank = conn.worksheet("Bank_Savings")
            bank_val = ws_bank.cell(2, 1).value
            bank_balance = float(bank_val) if bank_val else 0.0

        except Exception as e:
            st.error(f"ডাটা লোড করতে সমস্যা হয়েছে: {e}")
    
    # --- ২. চার্ট ও ডাটা প্রদর্শন ---
    total_all = total_savings + total_fdr + bank_balance

    if total_all > 0:
        # পাই চার্টের জন্য ডাটাফ্রেম
        chart_data = pd.DataFrame({
            "বিভাগ": ["মেম্বার সেভিংস", "FDR ইনভেস্টমেন্ট", "ব্যাংক ক্যাশ"],
            "পরিমাণ": [total_savings, total_fdr, bank_balance]
        })

        # ইউনিক ডোনাট চার্ট ডিজাইন
        fig = px.pie(chart_data, values='পরিমাণ', names='বিভাগ', hole=0.6,
                     color_discrete_sequence=['#38BDF8', '#8B5CF6', '#F59E0B'],
                     template="plotly_dark")
        
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- ৩. স্ট্যাটাস কার্ডস (আপনার আগের ডার্ক থিম স্টাইলে) ---
        st.markdown("""
            <style>
            .stat-card {
                background: #1E293B;
                padding: 15px;
                border-radius: 12px;
                border-top: 4px solid #38BDF8;
                text-align: center;
                margin-bottom: 10px;
            }
            .stat-val { color: white; font-size: 20px; font-weight: bold; }
            .stat-label { color: #94A3B8; font-size: 12px; }
            </style>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-label">মোট সেভিংস</div><div class="stat-val">৳{total_savings:,.0f}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card" style="border-top-color:#8B5CF6;"><div class="stat-label">মোট FDR</div><div class="stat-val">৳{total_fdr:,.0f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card" style="border-top-color:#F59E0B;"><div class="stat-label">ব্যাংক ব্যালেন্স</div><div class="stat-val">৳{bank_balance:,.0f}</div></div>', unsafe_allow_html=True)
            
    else:
        st.warning("আপনার গুগল শিটে বিশ্লেষণ করার মতো কোনো ডাটা পাওয়া যায়নি।")
