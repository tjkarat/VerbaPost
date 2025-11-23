import streamlit as st
import auth_engine
import time

def show_login(handle_login, handle_signup): 
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.title("VerbaPost 📮")
        st.subheader("Member Access")
        
        # Safe connection check
        try:
            client, err = auth_engine.get_supabase_client()
            if err:
                st.warning(f"Database Connection Issue: {err}")
        except Exception as e:
            st.error(f"System Error: {e}")

        tab_login, tab_signup = st.tabs(["Log In", "Create Account"]) 

        # --- LOGIN TAB ---
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", key="l_email")
                password = st.text_input("Password", type="password", key="l_pass")
                
                if st.form_submit_button("Log In", type="primary", use_container_width=True):
                    with st.spinner("Verifying..."):
                        handle_login(email, password)

        # --- SIGN UP TAB ---
        with tab_signup:
            with st.form("signup_form"):
                st.caption("Create your secure account")
                new_email = st.text_input("Email", key="s_email")
                
                c_p1, c_p2 = st.columns(2)
                new_pass = c_p1.text_input("Password", type="password", key="s_pass")
                confirm_pass = c_p2.text_input("Confirm Password", type="password", key="s_conf")

                st.markdown("---")
                st.caption("Return Address")
                
                new_name = st.text_input("Full Name", key="s_name")
                new_street = st.text_input("Street Address", key="s_street")
                c_a, c_b = st.columns(2)
                new_city = c_a.text_input("City", key="s_city")
                new_state = c_b.text_input("State", max_chars=2, key="s_state")
                new_zip = st.text_input("Zip Code", max_chars=5, key="s_zip")
                
                # LANGUAGE SELECTION (Crucial for font choice)
                st.markdown("---")
                st.caption("Formatting Preference")
                new_lang = st.selectbox("Preferred Language:", ["English", "Japanese", "Chinese", "Korean"], key="s_lang")
                
                if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                    if new_pass != confirm_pass:
                        st.error("❌ Passwords do not match.")
                    elif not (new_name and new_street and new_city and new_state and new_zip):
                        st.error("❌ Please fill all address fields.")
                    else:
                        with st.spinner("Creating account..."):
                            # PASSING ALL 8 ARGUMENTS
                            handle_signup(new_email, new_pass, new_name, new_street, new_city, new_state, new_zip, new_lang)
        
        st.divider()
        if st.button("⬅️ Back to Home", type="secondary"):
            st.session_state.current_view = "splash"
            st.rerun()