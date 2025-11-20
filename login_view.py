import streamlit as st
import time

def show_login(on_login_attempt, on_signup_attempt):
    """Renders the login form and accepts callback functions for login/signup."""
    
    # Center the login box
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.title("VerbaPost 📮")
        st.subheader("Member Access")
        
        # Test the button connection before showing forms
        if not on_login_attempt:
            st.error("⚠️ System initialization failed. Try refreshing.")
            st.stop()

        tab_login, tab_signup = st.tabs(["Log In", "Create Account"])

        # --- LOGIN TAB ---
        with tab_login:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            
            # The button now calls the external handler function
            if st.button("Log In", type="primary", use_container_width=True):
                with st.spinner("Verifying credentials..."):
                    on_login_attempt(email, password)

        # --- SIGN UP TAB ---
        with tab_signup:
            new_email = st.text_input("Email", key="new_email")
            new_pass = st.text_input("Password", type="password", key="new_pass")
            
            if st.button("Create Account", use_container_width=True):
                with st.spinner("Creating account..."):
                    on_signup_attempt(new_email, new_pass)
        
        st.divider()
        if st.button("⬅️ Back to Home", type="secondary"):
            st.session_state.current_view = "splash"
            st.rerun()