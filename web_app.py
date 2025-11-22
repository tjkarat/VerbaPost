import streamlit as st
from ui_splash import show_splash
from ui_main import show_main_app
from ui_login import show_login
from ui_admin import show_admin
import auth_engine 
import payment_engine

st.set_page_config(page_title="VerbaPost", page_icon="📮", layout="centered")

def inject_custom_css():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem !important; padding-bottom: 1rem !important;}
        div.stButton > button {border-radius: 8px; font-weight: 600; border: 1px solid #e0e0e0;}
        input {border-radius: 5px !important;}
        </style>
        """, unsafe_allow_html=True)
inject_custom_css()

# --- ROUTING ---
if "session_id" in st.query_params:
    st.session_state.current_view = "main_app"

if "current_view" not in st.session_state:
    st.session_state.current_view = "splash" 
if "user" not in st.session_state:
    st.session_state.user = None

# --- VIEW CONTROLLER ---
if st.session_state.current_view == "splash":
    show_splash()
elif st.session_state.current_view == "login":
    # Placeholder handlers for now since logic is inside views
    show_login(lambda e,p: None, lambda e,p,n,s,c,st,z: None) 
elif st.session_state.current_view == "admin":
    show_admin()
elif st.session_state.current_view == "main_app":
    with st.sidebar:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_view = "splash"
            st.rerun()
        if st.session_state.get("user"):
            st.caption(f"User: {st.session_state.user.user.email}")
            if st.session_state.user.user.email == "tjkarat@gmail.com": 
                if st.button("🔐 Admin", type="primary"):
                    st.session_state.current_view = "admin"
                    st.rerun()
            if st.button("Log Out"):
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()

    show_main_app()

# --- GLOBAL FOOTER ---
with st.sidebar:
    st.divider()
    st.markdown("📧 **Help:** support@verbapost.com")