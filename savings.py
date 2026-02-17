import streamlit as st
import json
import os
import pandas as pd

# --- ১. ডাটা ফাংশন (JSON ভিত্তিক) ---
SAVINGS_FILE = "savings_data.json"
MEMBERS_FILE = "members_data.json"

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- ২. কিস্তি জমার পপ-আপ (Add Deposit Dialog) ---
@st.dialog("Collect Savings")
def add_deposit():
    st.markdown("<h3 style='color:#1A365D;'>নতুন সঞ্চয় জমা করুন</h3>", unsafe_allow_html=True)
    members_data = load_json(MEMBERS_FILE)
    
    if not members_data:
        st.error("মেম্বার লিস্ট খালি! আগে মেম্বার যোগ করুন।")
        return

    names = [f"{m['Name']} (ID: {m['ID']})" for m in members_data]
    selected_member = st.selectbox("মেম্বার সিলেক্ট করুন", names)
    
    # মাস তৈরির লজিক (২৫-২৭ সাল)
    months = []
    for year in ["25", "26", "27"]:
        for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
            if year == "25" and m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]: continue
            if year == "27" and m in ["Nov", "Dec"]: continue
            months.append(f"{m}_{year}")
    
    selected_month = st.selectbox("মাস সিলেক্ট করুন", months)
    
    # অটো টাকা ক্যালকুলেশন (৫০০০ * শেয়ার)
    m_id = selected_member.split("(ID: ")[1].replace(")", "")
    member = next((m for m in members_data if str(m['ID']) == m_id), None)
    default_amt = int(member.get('Share', 1)) * 5000 if member else 0
    
    amount = st.text_input("জমার পরিমাণ (৫,০০০/শেয়ার)", value=str(default_amt))

    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
        data = load_json(SAVINGS_FILE)
        found = False
        for s in data:
            if str(s['ID']) == m_id:
                s[selected_month] = amount
                found = True
                break
        
        if not found:
            new_entry = {"ID": m_id, "Name": member['Name'], "Shares": member.get('Share', 1), selected_month: amount}
            data.append(new_entry)
            
        save_json(SAVINGS_FILE, data)
        st.success("সফলভাবে সেভ হয়েছে!")
        st.rerun()

# --- ৩. মেইন শো ফাংশন ---
def show():
    # CSS আইসোলেশন (যাতে মেইন ফাইলের লুক পরিবর্তন না হয়)
    st.markdown("""
        <style>
        /* সেভিংস পেজের ব্যাকগ্রাউন্ড */
        .savings-container {
            background-color: #F0F4F8;
            padding: 10px;
            border-radius: 10px;
        }
        
        /* হেডার ডিজাইন (#1A365D) */
        .savings-header {
            background-color: #1A365D;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            margin-bottom: 25px;
        }
        .header-text { color: white !important; font-family: 'Segoe UI'; font-weight: bold; margin: 0; font-size: 24px; }

        /* বড় বর্গাকার বাটন ডিজাইন (#2D3748) */
        div.savings-btn-group button {
            height: 100px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            background-color: #2D3748 !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* টেবিল ডিজাইন */
        thead tr th {
            background-color: #4A5568 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # কন্টেইনার শুরু
    st.markdown('<div class="savings-header"><h1 class="header-text">AL-BARAKAH SAVINGS LEDGER (2025-2027)</h1></div>', unsafe_allow_html=True)

    # বাটন সেকশন
    st.markdown('<div class="savings-btn-group">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 4])
    
    with col1:
        if st.button("➕\nADD SAVINGS", key="add_sav_btn"):
            add_deposit()
            
    with col2:
        if st.button("🔄\nSYNC MEMBERS", key="sync_sav_btn"):
            members_data = load_json(MEMBERS_FILE)
            current_savings = load_json(SAVINGS_FILE)
            existing_ids = {str(s['ID']) for s in current_savings}
            for m in members_data:
                if str(m['ID']) not in existing_ids:
                    current_savings.append({"ID": str(m['ID']), "Name": m['Name'], "Shares": m.get('Share', 1)})
            save_json(SAVINGS_FILE, current_savings)
            st.toast("মেম্বার ডাটা সিঙ্ক হয়েছে!", icon="✅")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ৪. ডাটা টেবিল (Full Data View)
    savings_data = load_json(SAVINGS_FILE)
    
    if savings_data:
        table_rows = []
        for s in savings_data:
            total_bal = 0
            last_p = "No Payment"
            
            # কিস্তি ক্যালকুলেশন
            for k, v in s.items():
                if k not in ['ID', 'Name', 'Shares'] and v not in ['', None, 0]:
                    try:
                        amt = float(str(v).replace(",", ""))
                        total_bal += amt
                        last_p = k.replace("_", " ")
                    except: continue
            
            table_rows.append({
                "ID": f"{int(s.get('ID', 0)):03d}",
                "Member Name": s.get('Name', 'N/A'),
                "Shares": s.get('Shares', 1),
                "Last Paid": last_p,
                "Total Balance": f"{total_bal:,.2f}"
            })

        df = pd.DataFrame(table_rows)
        
        # সার্চ বার
        search = st.text_input("🔍 মেম্বার খুঁজুন (নাম বা আইডি)", placeholder="Search here...")
        if search:
            df = df[df['Member Name'].str.contains(search, case=False) | df['ID'].contains(search)]

        # আপনার Treeview এর মতো স্ট্যাটিক টেবিল
        st.table(df)
    else:
        st.info("কোনো ডাটা পাওয়া যায়নি। SYNC MEMBERS বাটনে ক্লিক করুন।")
