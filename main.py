import streamlit as st
import os
import home, members, savings, statement, bank, ledger, receipts
import streamlit as st

# --- Swipe Gesture যোগ করার জন্য JavaScript কোড ---
swipe_js = """
<script>
    const doc = window.parent.document;
    let touchstartX = 0;
    let touchendX = 0;

    // আঙুল রাখা শুরু করলে
    doc.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
    }, false);

    // আঙুল সরানো শেষ করলে
    doc.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX;
        handleGesture();
    }, false);

    function handleGesture() {
        // বাম থেকে ডানে টান দিলে (সাইডবার ওপেন)
        if (touchendX - touchstartX > 100) {
            const sidebarButton = doc.querySelector('button[kind="headerNoPadding"]');
            if (sidebarButton) sidebarButton.click();
        }
        // ডান থেকে বামে টান দিলে (সাইডবার ক্লোজ)
        if (touchstartX - touchendX > 100) {
            const sidebarButton = doc.querySelector('button[kind="headerNoPadding"]');
            if (sidebarButton) sidebarButton.click();
        }
    }
</script>
"""

# অ্যাপে এই স্ক্রিপ্টটি রান করা
st.components.v1.html(swipe_js, height=0)

# আপনার বাকি কোড নিচে আগের মতোই থাকবে...
# ---------------- Page Configuration ----------------
st.set_page_config(
    page_title="Al-Barakah Management Pro",
    page_icon="🏢",
    layout="wide"
)

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
    .stApp { background-color: #1c2b36 !important; }
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }
    .sidebar-title {
        color: #22c55e;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        margin-top: 20px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 6px !important;
        border: 1px solid #2d3e4b !important;
        background-color: #0C001C;
        color: #cfd8dc !important;
        font-size: 16px !important;
        text-align: left;
        padding: 8px 15px !important;
        margin-bottom: 5px !important;
        transition: 0.3s all ease;
    }
    .stButton > button:hover {
        border: 1px solid #22c55e !important;
        color: #22c55e !important;
        transform: translateX(5px);
    }
    /* লগইন পেজের বাটনগুলো সেন্টারে রাখা */
    .login-header {
        text-align: center;
        color: #22c55e;
        margin-bottom: 20px;
    }
    [data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- Session State ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = "Member"
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# ---------------- Login Logic ----------------
def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 class='login-header'>AL-BARAKAH LOGIN</h1>", unsafe_allow_html=True)
        
        # পাশাপাশি বাটন (Role Selection)
        role_col1, role_col2 = st.columns(2)
        with role_col1:
            if st.button("👤 MEMBER", use_container_width=True):
                st.session_state.role = "Member"
        with role_col2:
            if st.button("🔑 ADMIN", use_container_width=True):
                st.session_state.role = "Admin"

        st.info(f"Currently Selected: **{st.session_state.role}**")

        with st.form("login_form"):
            user_id = st.text_input(f"{st.session_state.role} ID")
            password = st.text_input("Password", type="password")
            login_submit = st.form_submit_button(f"Login as {st.session_state.role}", use_container_width=True)

            if login_submit:
                if st.session_state.role == "Admin" and user_id == "admin" and password == "abbs2027":
                    st.session_state.logged_in = True
                    st.rerun()
                elif st.session_state.role == "Member" and password == "12345":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")

# ---------------- App Logic ----------------
if not st.session_state.logged_in:
    login_page()
else:
    with st.sidebar:
        st.markdown('<div class="sidebar-title">AL-BARAKAH</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='color: #22c55e; text-align: center;'>Mode: {st.session_state.role}</p>", unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.role == "Admin":
            pages = {
                "🏠 Home": home, 
                "👤 Member Identity": members, 
                "💰 Monthly Savings": savings, 
                "📊 Member Statement": statement, 
                "🏦 Bank Data": bank, 
                "📒 Ledger": ledger,
                "🧾 Receipts": receipts
            }
        else:
            pages = {
                "🏠 Home": home, 
                "👤 Member Identity": members, 
                "📊 Member Statement": statement, 
                "🏦 Bank Data": bank, 
                "📒 Ledger": ledger,
            }

        for name in pages:
            if st.button(name, key=name, use_container_width=True):
                st.session_state.page = name
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    pages[st.session_state.page].show()
