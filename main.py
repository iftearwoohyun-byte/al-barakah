import streamlit as st
import os
import home, members, savings, statement, bank, ledger, receipts
import streamlit as st

# --- Force Close & Swipe JavaScript ---
final_js = """
<script>
    const doc = window.parent.document;

    // ১. সাইডবার বন্ধ করার মেইন ফাংশন
    function closeSidebar() {
        // স্ট্রীমলিটের সাইডবার বাটন ধরার ৩টি সম্ভাব্য উপায়
        const btn1 = doc.querySelector('button[kind="headerNoPadding"]');
        const btn2 = doc.querySelector('[data-testid="stSidebarCollapseButton"]');
        
        // যদি বাটন পাওয়া যায় এবং সাইডবার ওপেন থাকে (বাটনটি তখন ক্লোজ আইকন দেখায়)
        if (btn1) {
            btn1.click();
        } else if (btn2) {
            btn2.click();
        }
    }

    // ২. মেনু আইটেমে ক্লিক করলে অটো হাইড
    // একটু সময় পর পর চেক করবে সাইডবার মেনু তৈরি হয়েছে কি না
    setInterval(() => {
        const navItems = doc.querySelectorAll('[data-testid="stSidebarNav"] a, [data-testid="stSidebarNav"] button');
        navItems.forEach(item => {
            if (!item.getAttribute('data-click-listener')) {
                item.addEventListener('click', () => {
                    setTimeout(closeSidebar, 300); // ক্লিক করার ০.৩ সেকেন্ড পর বন্ধ হবে
                });
                item.setAttribute('data-click-listener', 'true');
            }
        });
    }, 1000);

    // ৩. সোয়াইপ গেসচার (৫০ পিক্সেল)
    let touchstartX = 0;
    doc.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
    }, {passive: true});

    doc.addEventListener('touchend', e => {
        let touchendX = e.changedTouches[0].screenX;
        let diff = touchendX - touchstartX;
        
        const sidebar = doc.querySelector('[data-testid="stSidebar"]');
        const isExpanded = sidebar ? sidebar.getAttribute('aria-expanded') === 'true' : false;

        // বাম থেকে ডানে টানলে এবং সাইডবার বন্ধ থাকলে -> ওপেন হবে
        if (diff > 50 && !isExpanded) {
            closeSidebar();
        }
        // ডান থেকে বামে টানলে এবং সাইডবার খোলা থাকলে -> বন্ধ হবে
        if (diff < -50 && isExpanded) {
            closeSidebar();
        }
    }, {passive: true});
</script>
"""

st.components.v1.html(final_js, height=0)

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
