import streamlit as st

def show_splash():
    P_STANDARD = "$2.99"
    P_HEIRLOOM = "$5.99"
    P_CIVIC = "$6.99"

    # --- HERO ---
    st.title("VerbaPost 📮")
    st.subheader("Turn your voice into a real letter.") # <--- CONFIRMED
    st.markdown("##### Texts are trivial. Emails are ignored. Real letters get read.")
    
    st.divider()
    
    # ... (Rest of the file is the Native Container version from before)
    # I'm truncating for brevity, but ensure the rest of the file (Pricing/CTA) is there.
    # If you need the full file again, let me know.

    # --- HOW IT WORKS ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("🎙️ **1. Dictate**")
        st.caption("Tap the mic. AI handles the typing.")
    with c2:
        st.warning("✍️ **2. Sign**")
        st.caption("Review the text, sign on screen.")
    with c3:
        st.success("📮 **3. We Mail**")
        st.caption("We print, stamp, and mail it.")

    st.divider()

    # --- PRICING ---
    st.subheader("Simple Pricing")
    st.markdown("""
    <style>
        [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            color: #E63946 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)
    with p1:
        with st.container(border=True):
            st.markdown("### ⚡ Standard")
            st.metric(label="Price", value=P_STANDARD, label_visibility="collapsed")
            st.caption("API Fulfillment • Window Envelope • Mailed in 24hrs")
    with p2:
        with st.container(border=True):
            st.markdown("### 🏺 Heirloom")
            st.metric(label="Price", value=P_HEIRLOOM, label_visibility="collapsed")
            st.caption("Hand-Stamped • Premium Paper • Mailed from Nashville")
    with p3:
        with st.container(border=True):
            st.markdown("### 🏛️ Civic Blast")
            st.metric(label="Price", value=P_CIVIC, label_visibility="collapsed")
            st.caption("Activism Mode • Auto-Find Reps • Mails Senate + House")

    st.divider()

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