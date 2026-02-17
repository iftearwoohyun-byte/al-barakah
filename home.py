import streamlit as st
import os
import base64

def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def show():
    # ১. লোগো একদম সেন্টারে আনার জন্য HTML/CSS
    if os.path.exists("logo.png"):
        img_base64 = get_image_base64("logo.png")
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; padding-top: 20px;">
                <img src="data:image/png;base64,{img_base64}" style="width: 150px; border-radius: 10px;">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown("<h1 style='text-align: center;'>🏢</h1>", unsafe_allow_html=True)

    # ২. টাইটেল
    st.markdown(
        "<h1 style='text-align:center; color:white; margin-top: 10px;'>Welcome to Al-Barakah Management System</h1>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ৩. ডাটা কার্ডস সেকশন
    col1, col2, col3 = st.columns(3)

    def card(title, value):
        st.markdown(f"""
        <div style="
            background-color:#33475b;
            padding:30px;
            border-radius:12px;
            text-align:center;
            border: 1px solid #2d3e4b;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        ">
            <h4 style="color:#a3b1bb; margin-bottom:10px; font-size: 18px;">{title}</h4>
            <h2 style="color:#22c55e; margin:0; font-size: 32px;">{value}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col1:
        card("Active Members", "17")

    with col2:
        card("Total Shares", "20")

    with col3:
        card("Status", "Active")

    # ৪. মেইন ব্যাকগ্রাউন্ড এনশিওর করা
    st.markdown("""
        <style>
        .stApp {
            background-color: #1c2b36 !important;
        }
        </style>
    """, unsafe_allow_html=True)
