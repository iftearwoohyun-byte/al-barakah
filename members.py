import streamlit as st
import pandas as pd
import os
import base64
import io
from PIL import Image, ImageDraw, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database import get_live_data # সঠিক নাম ইমপোর্ট

def get_circular_img_b64(m_id, size=(300, 300)):
    img_path = "logo.png" 
    extensions = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
    for ext in extensions:
        temp = f"{m_id}{ext}" 
        if os.path.exists(temp):
            img_path = temp
            break
    if os.path.exists(img_path):
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
        except: pass
    if os.path.exists("logo.png"):
        logo_img = Image.open("logo.png").convert("RGBA").resize(size)
        buffered = io.BytesIO()
        logo_img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode(), "logo.png"
    return "", "logo.png"

def generate_pdf(member, member_img_path):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    if os.path.exists("logo.png"):
        c.drawImage("logo.png", 50, h-75, width=60, height=60, mask='auto')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(120, h-45, "Al-Barakah Business Society")
    if os.path.exists(member_img_path):
        c.drawImage(member_img_path, w-170, h-220, width=120, height=120, mask='auto')
    c.drawString(50, h-120, f"MEMBER ID: #{int(member.get('ID', 0)):02d}")
    c.drawString(50, h-145, str(member.get('Name', '')).upper())
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

@st.dialog("Member Profile")
def show_profile_popup(m):
    img_b64, img_path = get_circular_img_b64(m['ID'])
    col1, col2 = st.columns([1, 2])
    with col1: st.markdown(f'<img src="data:image/png;base64,{img_b64}" style="width:100%; border-radius:50%;">', unsafe_allow_html=True)
    with col2:
        st.header(m['Name'])
        st.write(f"**ID:** {int(m.get('ID',0))}")
        st.write(f"**Shares:** {m.get('Share', 0)}")
    pdf_file = generate_pdf(m, img_path)
    st.download_button("📥 DOWNLOAD PDF", data=pdf_file, file_name=f"{m['ID']}.pdf")

def show():
    st.markdown("<h1 style='text-align: center; color: #38BDF8;'>MEMBER DIRECTORY</h1>", unsafe_allow_html=True)
    members_list = get_live_data() # লাইভ ডাটা কল
    if not members_list:
        st.info("গুগল শিটে কোনো ডাটা নেই।")
        return
    search = st.text_input("মেম্বার আইডি বা নাম দিয়ে খুঁজুন")
    filtered = [m for m in members_list if search.lower() in str(m['Name']).lower() or str(m['ID']) == search]
    cols = st.columns(4)
    for i, m in enumerate(filtered):
        with cols[i % 4]:
            img_b64, _ = get_circular_img_b64(m['ID'])
            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img_b64}" style="width:100px; height:100px; border-radius:50%;"><br><b>{m["Name"]}</b><br>Share: {m["Share"]}</div>', unsafe_allow_html=True)
            if st.button("View Profile", key=f"btn_{m['ID']}", use_container_width=True):
                show_profile_popup(m)
