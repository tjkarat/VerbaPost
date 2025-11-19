import streamlit as st
# UPDATED IMPORTS: No more 'views.' prefix
from splash_view import show_splash
from main_app_view import show_main_app

# --- PAGE CONFIG ---
st.set_page_config(page_title="VerbaPost", page_icon="📮", layout="centered")

# --- NAVIGATION STATE ---
if "current_view" not in st.session_state:
    st.session_state.current_view = "splash" 

# --- ROUTER ---
if st.session_state.current_view == "splash":
    show_splash()

elif st.session_state.current_view == "main_app":
    # Add a "Back to Home" button in the sidebar
    with st.sidebar:
        if st.button("⬅️ Back to Home"):
            st.session_state.current_view = "splash"
            st.rerun()
        
    show_main_app()

elif st.session_state.current_view == "dashboard":
    st.title("Dashboard")
    st.info("Coming in the Subscription Tier Update")