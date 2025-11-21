import streamlit as st
import os

def show_splash():
    # --- CONFIG ---
    st.title("VerbaPost 📮")
    st.subheader("The Authenticity Engine.")
    st.markdown("##### Texts are trivial. Emails are ignored. Real letters get read.")
    
    st.divider()

    # --- HOW IT WORKS ---
    st.subheader("How it Works")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("🎙️ **1. Dictate**")
        st.caption("Tap the mic. AI handles the typing.")
    with c2:
        st.markdown("✍️ **2. Sign**")
        st.caption("Review the text, sign your name on screen.")
    with c3:
        st.markdown("📮 **3. We Mail**")
        st.caption("We print, stamp, and mail it.")

    st.divider()

    # --- PRICING TIERS (READ FROM FILE) ---
    st.subheader("Simple Pricing")
    
    try:
        with open("splash.html", "r") as f:
            html_content = f.read()
            st.markdown(html_content, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading pricing display: {e}")

    st.divider()

    # --- CTA ---
    col_spacer, col_btn, col_spacer2 = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🚀 Create My Account", type="primary", use_container_width=True):
            st.session_state.current_view = "login"
            st.session_state.initial_mode = "signup"
            st.rerun()
        
        st.write("")
        
        if st.button("Already a member? Log In", type="secondary", use_container_width=True):
            st.session_state.current_view = "login"
            st.session_state.initial_mode = "login"
            st.rerun()
