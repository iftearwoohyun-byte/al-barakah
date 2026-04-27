import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import database as db 

# --- ১. গুগল শিট থেকে সরাসরি ডাটা লোড ---
def load_data_from_gsheet():
    conn = db.connect_db()
    if conn:
        try:
            # সরাসরি 'Savings' শিট থেকে ডাটা রিড করা হচ্ছে
            worksheet = conn.worksheet("Savings")
            data = worksheet.get_all_records()
            return data
        except Exception as e:
            st.error(f"Error reading Savings sheet: {e}")
            return []
    return []

MONTH_MAP = {
    "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April",
    "May": "May", "Jun": "June", "Jul": "July", "Aug": "August",
    "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December"
}

def get_full_month_name(text):
    for short, full in MONTH_MAP.items():
        if short in text:
            return text.replace(short, full)
    return text

# --- ২. PDF জেনারেশন (আপনার অরিজিনাল ডিজাইন ও ওয়াটারমার্কসহ) ---
def generate_bank_style_pdf(member):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    
    # লোগো ও ডিজাইন
    if os.path.exists("logo.png"):
        c.saveState()
        c.setFillAlpha(0.07)
        c.drawImage("logo.png", w/2 - 150, h/2 - 150, width=300, height=300, mask='auto')
        c.restoreState()
        c.drawImage("logo.png", 50, h-90, width=60, height=60, mask='auto')

    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(40, h-105, w-40, h-105) 
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w/2 + 20, h-55, "AL-BARAKAH BUSINESS SOCIETY")
    c.setFont("Helvetica", 10)
    c.drawCentredString(w/2 + 20, h-75, "Barahatia, Lohagara, Chattogram")
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(w/2 + 20, h-90, "Estd: 2025")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(w/2, h-125, " MEMBER STATEMENT")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, h-160, f"ACCOUNT HOLDER : {str(member.get('Name', '')).upper()}")
    c.drawString(50, h-175, f"MEMBER ID      : # {int(member.get('ID', 0)):03d}")
    
    c.setFont("Helvetica", 9)
    c.drawRightString(w-50, h-160, f"Date: {datetime.now().strftime('%d %b, %Y')}")

    y = h - 215
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y, "SL")
    c.drawString(100, y, "Description / Month")
    c.drawRightString(w-70, y, "Deposit (BDT)")
    c.line(50, y-5, w-50, y-5)

    y -= 25
    total = 0
    sl = 1
    # কলামের নাম শিট অনুযায়ী চেক করা হবে
    ignore_list = ['ID', 'Name', 'Shares', 'Share']
    
    c.setFont("Helvetica", 10)
    for k, v in member.items():
        if k not in ignore_list and v not in ['', '0', 0, None]:
            try:
                c.drawString(60, y, f"{sl:02d}")
                full_desc = get_full_month_name(k.replace("_", " "))
                c.drawString(100, y, f"Savings - {full_desc}")
                
                amt = float(str(v).replace(",", ""))
                c.drawRightString(w-70, y, f"{amt:,.2f}")
                total += amt
                sl += 1
                y -= 22
            except: continue

    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "TOTAL ACCUMULATED:")
    c.drawRightString(w-70, y, f"{total:,.2f} BDT")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- ৩. UI ড্যাশবোর্ড (আপনার অরিজিনাল সিএসএস লুক) ---
def show():
    st.markdown("""
        <style>
        .ledger-header { background-color: #2D3748; padding: 15px; text-align: center; border-radius: 5px; margin-bottom: 20px; }
        .header-text { color: #F7FAFC !important; font-weight: bold; margin: 0; }
        .total-box { text-align: right; padding: 15px; background-color: #F7FAFC; border: 1px solid #CBD5E0; border-radius: 5px; margin-top: 10px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ledger-header"><h2 class="header-text">📊 MEMBER LEDGER DASHBOARD</h2></div>', unsafe_allow_html=True)

    m_id = st.text_input("Search Member ID:", placeholder="Enter ID...")
    
    if m_id:
        # গুগল শিট থেকে ফ্রেশ ডাটা আনা হচ্ছে
        data = load_data_from_gsheet()
        member = next((s for s in data if str(s.get('ID', '')) == str(m_id)), None)
        
        if member:
            st.markdown(f"<h3 style='color:#2B6CB0;'>👤 ACCOUNT: {str(member.get('Name', '')).upper()}</h3>", unsafe_allow_html=True)
            
            table_data = []
            total = 0
            idx = 1
            ignore_list = ['ID', 'Name', 'Shares', 'Share']
            
            for k, v in member.items():
                if k not in ignore_list and v not in ['', '0', 0, None]:
                    try:
                        val = float(str(v).replace(",", ""))
                        full_desc = get_full_month_name(k.replace("_", " "))
                        table_data.append([f"{idx:02d}", f"Savings - {full_desc}", f"{val:,.2f}"])
                        total += val
                        idx += 1
                    except: continue
            
            st.table(pd.DataFrame(table_data, columns=["SL", "Description", "Amount (BDT)"]))

            st.markdown(f"""
                <div class="total-box">
                    <h3 style="color:#2F855A; margin:0;">Total Balance: {total:,.2f} BDT</h3>
                </div>
            """, unsafe_allow_html=True)

            st.divider()
            pdf_bytes = generate_bank_style_pdf(member)
            st.download_button("📥 DOWNLOAD STATEMENT", pdf_bytes, f"Statement_{m_id}.pdf", "application/pdf", use_container_width=True)
        else:
            st.error("❌ এই আইডি-র কোনো ডাটা গুগল শিটে পাওয়া যায়নি!")
