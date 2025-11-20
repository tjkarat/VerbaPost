import streamlit as st
from splash_view import show_splash
from main_app_view import show_main_app
from login_view import show_login
import auth_engine # <--- We import the crash-prone file ONLY HERE
import database # <--- And the database here
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="VerbaPost", page_icon="📮", layout="centered")

# --- CORE HANDLERS (The Logic that was previously causing the blank page) ---
def handle_login(email, password):
    """Calls auth_engine and handles session state on success/failure."""
    user, error = auth_engine.sign_in(email, password)
    if error:
        st.error(f"Login Failed: {error}")
    else:
        st.success("Welcome back!")
        st.session_state.user = user
        st.session_state.user_email = email
        
        # Load Saved Address
        saved_addr = auth_engine.get_current_address(email)
        if saved_addr:
            st.session_state["from_name"] = saved_addr.get("name", "")
            st.session_state["from_street"] = saved_addr.get("street", "")
            st.session_state["from_city"] = saved_addr.get("city", "")
            st.session_state["from_state"] = saved_addr.get("state", "")
            st.session_state["from_zip"] = saved_addr.get("zip", "")
            
        st.session_state.current_view = "main_app"
        st.rerun()

def handle_signup(email, password):
    """Calls auth_engine for signup and handles session state."""
    user, error = auth_engine.sign_up(email, password)
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
    # Pass the handler functions to the login view
    show_login(handle_login, handle_signup)

elif st.session_state.current_view == "main_app":
    # Removed Alpha tag and added navigation
    with st.sidebar:
        st.subheader("Navigation")
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_view = "splash"
            st.rerun()
        # Display User Status
        if st.session_state.user:
            st.caption(f"Logged in: {st.session_state.user_email}")
        
    show_main_app()