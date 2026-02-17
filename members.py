import streamlit as st
import pandas as pd
import os
import base64
import io
from PIL import Image, ImageDraw, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database import members_list

# --- ১. মোবাইলে ডাউনলোডের বিশেষ ফাংশন ---
def get_pdf_download_link(pdf_file, filename):
    b64 = base64.b64encode(pdf_file.getvalue()).decode()
    return f'''
    <a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="text-decoration:none;">
        <div style="background-color:#38BDF8; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:bold; cursor:pointer;">
            📥 DOWNLOAD FULL PROFILE (PDF)
        </div>
    </a>
    '''

# --- ২. ছবি প্রসেসিং (সরাসরি রুট থেকে) ---
def get_circular_img_b64(m_id, size=(300, 300)):
    img_path = "logo.png" 
    for ext in [".jpg", ".jpeg", ".png", ".JPG"]:
        temp = f"{m_id}{ext}" 
        if os.path.exists(temp):
            img_path = temp
            break
            
    try:
        img = Image.open(img_path).convert("RGBA")
        img = ImageOps.exif_transpose(img)
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
        return "", "logo.png"

# --- ৩. PDF জেনারেটর ---
def generate_pdf(member, member_img_path):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    if os.path.exists("logo.png"):
        c.drawImage("logo.png", 50, h-75, width=60, height=60, mask='auto')
    c.setFont("Helvetica-Bold", 18)
    c.drawString(120, h-50, "Al-Barakah Business Society")
    c.line(50, h-85, w-50, h-85)
    
    if os.path.exists(member_img_path):
        c.drawImage(member_img_path, w-170, h-220, width=120, height=120, mask='auto')
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, h-130, f"MEMBER ID: #{member.get('ID', 0)}")
    c.drawString(50, h-155, str(member.get('Name', '')).upper())
    
    c.showPage(); c.save(); buffer.seek(0)
    return buffer

# --- ৪. প্রোফাইল পপ-আপ ---
@st.dialog("Member Full Profile")
def show_profile_popup(m):
    img_b64, img_path = get_circular_img_b64(m['ID'])
    st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:150px; border-radius:50%; border:3px solid #38BDF8;"></center>', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;'>{m['Name']}</h3>", unsafe_allow_html=True)
    
    st.divider()
    pdf_file = generate_pdf(m, img_path)
    # নতুন ডাউনলোড লিংক ব্যবহার
    st.markdown(get_pdf_download_link(pdf_file, f"Profile_{m['ID']}.pdf"), unsafe_allow_html=True)

# --- ৫. মেইন পেজ ---
def show():
    st.markdown("<h1 style='text-align: center; color: #38BDF8;'>MEMBER DIRECTORY</h1>", unsafe_allow_html=True)
    search = st.text_input("মেম্বার আইডি বা নাম দিয়ে খুঁজুন...")
    filtered = [m for m in members_list if search.lower() in m['Name'].lower() or str(m['ID']) == search]
    
    cols = st.columns(4)
    for i, m in enumerate(filtered):
        with cols[i % 4]:
            img_b64, _ = get_circular_img_b64(m['ID'])
            st.markdown(f'''<div style="background-color:#1E293B; border-radius:15px; padding:15px; text-align:center; margin-bottom:10px;">
                <img src="data:image/png;base64,{img_b64}" style="width:100px; height:100px; border-radius:50%; border:2px solid #38BDF8;">
                <div style="color:white; font-weight:bold; margin-top:10px; height:40px;">{m['Name']}</div>
            </div>''', unsafe_allow_html=True)
            if st.button(f"View Profile", key=f"btn_{m['ID']}", use_container_width=True):
                show_profile_popup(m)
