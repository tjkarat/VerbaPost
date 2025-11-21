import streamlit as st
# CHANGED IMPORT:
from view_splash import show_splash
from main_app_view import show_main_app
from login_view import show_login
import auth_engine 
import database 
import urllib.parse
import payment_engine

# --- PAGE CONFIG ---
st.set_page_config(page_title="VerbaPost", page_icon="📮", layout="centered")

# --- CSS INJECTOR ---
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

# --- HANDLER FUNCTIONS ---
def handle_login(email, password):
    user, error = auth_engine.sign_in(email, password)
    if error:
        st.error(f"Login Failed: {error}")
    else:
        st.success("Welcome back!")
        st.session_state.user = user
        st.session_state.user_email = email
        saved_addr = auth_engine.get_current_address(email)
        if saved_addr:
            st.session_state["from_name"] = saved_addr.get("name", "")
            st.session_state["from_street"] = saved_addr.get("street", "")
            st.session_state["from_city"] = saved_addr.get("city", "")
            st.session_state["from_state"] = saved_addr.get("state", "")
            st.session_state["from_zip"] = saved_addr.get("zip", "")
        st.session_state.current_view = "main_app"
        st.rerun()

def handle_signup(email, password, name, street, city, state, zip_code):
    user, error = auth_engine.sign_up(email, password, name, street, city, state, zip_code)
    if error:
        st.error(f"Error: {error}")
    else:
        st.success("Account created! Logged in.")
        st.session_state.user = user
        st.session_state.user_email = email
        st.session_state.current_view = "main_app"
        st.rerun()

# --- ROUTING LOGIC ---
if "session_id" in st.query_params:
    session_id = st.query_params["session_id"]
    if payment_engine.check_payment_status(session_id):
        st.session_state.current_view = "main_app"
        st.session_state.payment_complete = True
        st.toast("✅ Payment Confirmed!")
        st.query_params.clear() 

if "current_view" not in st.session_state:
    st.session_state.current_view = "splash" 
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.current_view == "splash":
    show_splash()

elif st.session_state.current_view == "login":
    show_login(handle_login, handle_signup)

elif st.session_state.current_view == "main_app":
    with st.sidebar:
        st.subheader("Navigation")
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_view = "splash"
            st.rerun()
        if st.session_state.user:
            st.caption(f"Logged in: {st.session_state.user_email}")
        
    show_main_app()