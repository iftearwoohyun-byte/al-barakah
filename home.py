import streamlit as st
import pandas as pd
from datetime import datetime
import database as db

def get_home_stats():
    conn = db.connect_db()
    stats = {"savings": 0, "fdr": 0, "last_fdr": "N/A", "fine": 0}
    
    if conn:
        try:
            # ১. মোট সঞ্চয় (Savings)
            ws_s = conn.worksheet("Savings")
            # get_all_values ব্যবহার করলে ডুপ্লিকেট হেডারের সমস্যা হয় না
            s_data = ws_s.get_all_values()
            if len(s_data) > 1:
                df_s = pd.DataFrame(s_data[1:], columns=s_data[0])
                # অপ্রয়োজনীয় কলাম বাদ দিয়ে সব সংখ্যার যোগফল
                exclude = ['ID', 'Name', 'Shares', 'Total', 'Remarks', 'Fine']
                val_cols = [c for c in df_s.columns if c and c not in exclude]
                for col in val_cols:
                    stats["savings"] += pd.to_numeric(df_s[col].str.replace(',', ''), errors='coerce').sum()

            # ২. FDR এমাউন্ট ও শেষ তারিখ (FDR_Data)
            ws_f = conn.worksheet("FDR_Data")
            f_data = ws_f.get_all_values()
            if len(f_data) > 1:
                df_f = pd.DataFrame(f_data[1:], columns=f_data[0])
                stats["fdr"] = pd.to_numeric(df_f['Amount'].str.replace(',', ''), errors='coerce').sum()
                
                # শেষ FDR মাস বের করা
                if 'Open_Date' in df_f.columns:
                    df_f['dt'] = pd.to_datetime(df_f['Open_Date'], errors='coerce')
                    last_row = df_f.sort_values('dt').iloc[-1]
                    stats["last_fdr"] = last_row['dt'].strftime("%B %Y") if not pd.isnull(last_row['dt']) else "N/A"

            # ৩. মোট জরিমানা (Late Fee)
            try:
                ws_l = conn.worksheet("Late Fee")
                l_vals = ws_l.get_all_values()
                # শিটের সব ঘর থেকে শুধু সংখ্যাগুলো যোগ করা
                for row in l_vals:
                    for val in row:
                        try:
                            clean_v = str(val).replace(',', '').strip()
                            if clean_v: stats["fine"] += float(clean_v)
                        except: continue
            except: pass
            
        except Exception as e:
            st.error(f"Data Connection Error: {e}")
            
    return stats
