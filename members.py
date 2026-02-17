import streamlit as st
import pandas as pd
import os
import base64
import io
from PIL import Image, ImageDraw, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database import members_list

# --- ১. ছবি প্রসেসিং (সরাসরি রুট ডিরেক্টরি থেকে ছবি খোঁজা) ---
def get_circular_img_b64(m_id, size=(300, 300)):
    # ডিফল্ট ছবি হিসেবে লোগো সেট করা
    img_path = "logo.png" 
    
    # মেম্বার আইডি অনুযায়ী সরাসরি ফাইল চেক করা (যেমন: 1.jpg, 2.png)
    extensions = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
    
    for ext in extensions:
        temp = f"{m_id}{ext}" 
        if os.path.exists(temp):
            img_path = temp
            break
            
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path).convert("RGBA")
            img = ImageOps.exif_transpose(img) # মোবাইল ছবির রোটেশন ফিক্স
            img = img.resize(size, Image.Resampling.LANCZOS)
            
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            
            output = Image.new('RGBA', size, (0, 0, 0, 0))
            output.paste(img, (0, 0), mask=mask)
            
            buffered = io.BytesIO()
            output.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode(), img_path
        except:
            pass

    # যদি মেম্বার ছবি না পাওয়া যায়, তবে লোগো দেখাবে
    if os.path.exists("logo.png"):
        logo_img = Image.open("logo.png").convert("RGBA").resize(size)
        buffered = io.BytesIO()
        logo_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode(), "logo.png"
        
    return "", "logo.png"

# --- ২. PDF জেনারেটর (সরাসরি ইমেজ পাথ ব্যবহার) ---
def generate_pdf(member, member_img_path):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    
    # হেডার লোগো
    if os.path.exists("logo.png"):
        c.drawImage("logo.png", 50, h-75, width=60, height=60, mask='auto')

    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0, 0.2, 0.4)
    c.drawString(120, h-45, "Al-Barakah Business Society")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(120, h-60, "Barahatia, Lohagara, Chattogram | Estd. 2025")
    c.line(50, h-85, w-50, h-85)

    # মেম্বার ছবি (সরাসরি মেইন ফোল্ডার থেকে)
    if os.path.exists(member_img_path):
        c.drawImage(member_img_path, w-170, h-220, width=120, height=120, mask='auto')

    # মেম্বার বেসিক তথ্য
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0.8, 0.3, 0)
    c.drawString(50, h-120, f"MEMBER ID: #{member.get('ID', 0):02d}")
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, h-145, str(member.get('Name', '')).upper())

    details = [
        ("Father's Name", member.get('Father', 'N/A')),
        ("Mother's Name", member.get('Mother', 'N/A')),
        ("Date of Birth", member.get('DOB', 'N/A')),
        ("Occupation", member.get('Occupation', 'N/A')),
        ("Mobile Number", member.get('Mobile', 'N/A')),
        ("NID / Passport", member.get('NID', 'N/A')),
        ("Total Shares", f"{member.get('Share', 0)} Units"),
        ("Nominee Name", member.get('Nominee', 'N/A')),
        ("Nominee ID/NID", member.get('Nominee_ID', 'N/A')),
        ("Present Address", member.get('Present', 'N/A')),
        ("Permanent Address", member.get('Permanent', 'N/A')),
    ]
    
    curr_y = h - 250
    for label, val in details:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, curr_y, label)
        c.setFont("Helvetica", 11)
        c.drawString(180, curr_y, f":  {val}")
        curr_y -= 28 

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- ৩. প্রোফাইল পপ-আপ ---
@st.dialog("Member Full Profile")
def show_profile_popup(m):
    img_b64, img_path = get_circular_img_b64(m['ID'])
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<img src="data:image/png;base64,{img_b64}" style="width:100%; border-radius:15px; border:3px solid #38BDF8;">', unsafe_allow_html=True)
    with col2:
        st.header(m['Name'])
        st.subheader(f"ID: #{m.get('ID', 0):02d}")
        st.write(f"**Shares:** {m.get('Share', 0)} Units")

    st.divider()
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.write(f"**Father:** {m.get('Father', 'N/A')}")
        st.write(f"**Mother:** {m.get('Mother', 'N/A')}")
        st.write(f"**Mobile:** {m.get('Mobile', 'N/A')}")
    with d_col2:
        st.write(f"**DOB:** {m.get('DOB', 'N/A')}")
        st.write(f"**Occupation:** {m.get('Occupation', 'N/A')}")
        st.write(f"**NID:** {m.get('NID', 'N/A')}")
    
    st.info(f"📍 Present Address: {m.get('Present', 'N/A')}")

    pdf_file = generate_pdf(m, img_path)
    st.download_button(
        label="📥 DOWNLOAD FULL PROFILE (PDF)",
        data=pdf_file,
        file_name=f"Profile_{m['ID']}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# --- ৪. মেইন মেম্বার পেইজ ---
def show():
    st.markdown("<h1 style='text-align: center; color: #38BDF8;'>MEMBER DIRECTORY</h1>", unsafe_allow_html=True)

    st.markdown("""
        <style>
        .m-card {
            background-color: #1E293B;
            border: 2px solid #334155;
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            min-height: 270px;
        }
        .m-img {
            width: 130px;
            height: 130px;
            border-radius: 50%;
            border: 3px solid #38BDF8;
            object-fit: cover;
            margin-bottom: 10px;
        }
        .m-name { color: white; font-size: 18px; font-weight: bold; margin-bottom: 5px; height: 50px; overflow: hidden; }
        .m-share { color: #22C55E; font-size: 16px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    search = st.text_input("মেম্বার আইডি বা নাম দিয়ে খুঁজুন...", placeholder="উদা: 101 বা Mamun")
    
    # সার্চ লজিক
    filtered = [m for m in members_list if search.lower() in m['Name'].lower() or str(m['ID']) == search]

    cols = st.columns(4)
    for i, m in enumerate(filtered):
        with cols[i % 4]:
            img_b64, _ = get_circular_img_b64(m['ID'])
            st.markdown(f"""
                <div class="m-card">
                    <img src="data:image/png;base64,{img_b64}" class="m-img">
                    <div class="m-name">{m['Name']}</div>
                    <div class="m-share">Shares: {m['Share']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"View Profile", key=f"btn_{m['ID']}", use_container_width=True):
                show_profile_popup(m)
