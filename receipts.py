import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import io
import zipfile

# --- Configuration (আপনার কোড অনুযায়ী) ---
SOCIETY_NAME = "Al-Barakah Business Society"
ADDRESS = "Barahatia, Lohagara, Chattogram"
SHARE_VALUE = 5000
THANKS_MSG = "May Allah grant barakah in your wealth."
LOGO_FILE = "logo.png"
SIGN_FILE = "signature.png"

# মেম্বার লিস্ট (যদি ডাটাবেস ফাইল না থাকে তবে ডেমো ডাটা)
try:
    from database import members_list
except:
    members_list = [
        {"ID": 1, "Name": "Sample Member", "Share": 1}
    ]

def create_receipt_image(member, month, year):
    """রসিদ ইমেজ তৈরির মূল লজিক (আপনার Pillow কোড)"""
    w, h = 3000, 2000 
    canvas = Image.new('RGB', (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    
    # Fonts loading (Streamlit এর জন্য ফন্ট ফাইল না থাকলে default নেবে)
    try:
        f_title = ImageFont.truetype("arialbd.ttf", 140)
        f_header = ImageFont.truetype("arial.ttf", 65)
        f_label = ImageFont.truetype("arialbd.ttf", 80)
        f_value = ImageFont.truetype("arial.ttf", 80)
        f_islamic = ImageFont.truetype("ariali.ttf", 55) 
    except:
        f_title = f_header = f_label = f_value = f_islamic = ImageFont.load_default()

    # ১. বর্ডার ও ডিজাইন
    draw.rectangle([40, 40, w-40, h-40], outline=(0, 51, 102), width=25) # Navy Blue
    draw.rectangle([80, 80, w-80, h-80], outline=(218, 165, 32), width=8) # Gold
    draw.rectangle([88, 88, w-88, 500], fill=(240, 245, 255))

    # ২. লোগো
    if os.path.exists(LOGO_FILE):
        logo = Image.open(LOGO_FILE).convert("RGBA").resize((320, 320))
        canvas.paste(logo, (180, 130), logo)

    # ৩. হেডার
    draw.text((w//2 + 150, 220), SOCIETY_NAME, fill=(0, 51, 102), font=f_title, anchor="mm")
    draw.text((w//2 + 150, 350), ADDRESS, fill=(80, 80, 80), font=f_header, anchor="mm")
    
    draw.rectangle([w//2 - 500, 550, w//2 + 500, 680], fill=(0, 51, 102))
    draw.text((w//2, 615), "PAYMENT RECEIPT", fill=(255, 255, 255), font=f_label, anchor="mm")

    # ৪. ডাটা সেকশন
    amount = member['Share'] * SHARE_VALUE
    date_str = datetime.now().strftime("%d %B, %Y")
    
    data_points = [
        ("Member Name", member['Name']),
        ("Member ID", f"{member['ID']:03d}"),
        ("Number of Shares", str(member['Share'])),
        ("Payment Month", f"{month}, {year}"),
        ("Issuing Date", date_str),
        ("Paid Amount", f"{amount:,} BDT")
    ]

    start_y = 850
    for i, (lbl, val) in enumerate(data_points):
        curr_y = start_y + (i * 130)
        draw.line([400, curr_y + 90, w-400, curr_y + 90], fill=(200, 200, 200), width=2)
        draw.text((450, curr_y), lbl, fill=(50, 50, 50), font=f_label)
        draw.text((1150, curr_y), ":", fill=(0, 0, 0), font=f_label)
        draw.text((1250, curr_y), val, fill=(0, 0, 0), font=f_value)

    # ৫. ইসলামিক মেসেজ
    draw.text((w//2, 1750), THANKS_MSG, fill=(0, 102, 51), font=f_islamic, anchor="mm")

    # ৬. সিগনেচার
    if os.path.exists(SIGN_FILE):
        sign = Image.open(SIGN_FILE).convert("RGBA").resize((450, 180))
        canvas.paste(sign, (2150, 1550), sign)
    
    draw.line([2100, 1720, 2750, 1720], fill=(0, 0, 0), width=7)
    draw.text((2425, 1770), "Collector Signature", fill=(0, 0, 0), font=f_header, anchor="mm")

    return canvas

def show():
    st.markdown("""
        <style>
        .stApp { background-color: #F8FAFC; }
        .receipt-header { background-color: #1A365D; padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 25px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="receipt-header"><h1>🧾 Bulk Receipt Generation</h1></div>', unsafe_allow_html=True)

    # ইনপুট ফর্ম
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Select Year", ["2025", "2026", "2027"])
        with col2:
            month = st.selectbox("Select Month", ["January", "February", "March", "April", "May", "June", 
                                                "July", "August", "September", "October", "November", "December"])

    if st.button("🚀 START BATCH GENERATION", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for idx, member in enumerate(members_list):
                # ইমেজ তৈরি
                receipt_img = create_receipt_image(member, month, year)
                
                # ইমেজ মেমরিতে সেভ করা (হার্ডড্রাইভে না জমিয়ে সরাসরি বাফারে)
                img_byte_arr = io.BytesIO()
                receipt_img.save(img_byte_arr, format='JPEG', quality=90)
                
                # জিপ ফাইলে যোগ করা
                file_name = f"Receipt_{member['ID']}_{month}.jpg"
                zip_file.writestr(file_name, img_byte_arr.getvalue())
                
                # প্রগ্রেস আপডেট
                progress_bar.progress((idx + 1) / len(members_list))
        
        st.success(f"Successfully generated {len(members_list)} receipts!")
        
        # জিপ ডাউনলোড বাটন
        st.download_button(
            label="📥 DOWNLOAD ALL RECEIPTS (ZIP)",
            data=zip_buffer.getvalue(),
            file_name=f"Receipts_{month}_{year}.zip",
            mime="application/x-zip-compressed",
            use_container_width=True
        )

        # একটি ডেমো প্রিভিউ দেখানো
        st.markdown("### Preview (Last Generated):")
        st.image(receipt_img, caption=f"Receipt Preview for {members_list[-1]['Name']}", use_container_width=True)
