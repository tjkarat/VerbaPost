import streamlit as st

# Version 18.0 - SEO & Targeting Update
def show_splash():
    # --- CONFIG ---
    P_STANDARD = "$2.99"
    P_HEIRLOOM = "$5.99"
    P_CIVIC = "$6.99"

    # --- HERO (H1 - Main Keywords) ---
    st.title("VerbaPost 📮")
    st.subheader("Send Physical Mail from your Phone.")
    st.markdown("##### Dictate letters, upload photos, and we print & mail them for you.")
    
    st.divider()

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
    
    # --- USE CASES (SEO HEAVY SECTION) ---
    st.subheader("Who uses VerbaPost?")
    
    u1, u2, u3 = st.columns(3)
    
    with u1:
        st.markdown("### 🧡 Families & Inmates")
        st.markdown("""
        Stay connected with loved ones in **Prison or Jail**. 
        * Send letters without buying stamps.
        * **Mail photos** easily from your phone.
        * Compliant with correctional facility mail rules (White paper, standard envelope).
        """)

    with u2:
        st.markdown("### 🏡 Realtors & Sales")
        st.markdown("""
        Stand out with **Handwritten Direct Mail**.
        * Perfect for **Real Estate Prospecting**.
        * "Heirloom" tier uses real ink and stamps for high open rates.
        * Follow up with leads personally, instantly.
        """)

    with u3:
        st.markdown("### 🗳️ Civic Activists")
        st.markdown("""
        Make your voice heard in Washington.
        * **Write to Congress** and the Senate instantly.
        * Our **Civic Blast** feature auto-detects your representatives.
        * Send physical petitions that can't be ignored like email.
        """)

    st.divider()

    # --- PRICING TIERS ---
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
            st.caption("For: **Inmate Mail**, Business Invoices, Quick Notes.")

    with p2:
        with st.container(border=True):
            st.markdown("### 🏺 Heirloom")
            st.metric(label="Price", value=P_HEIRLOOM, label_visibility="collapsed")
            st.caption("For: **Real Estate Marketing**, Love Letters, Thank You Notes.")

    with p3:
        with st.container(border=True):
            st.markdown("### 🏛️ Civic Blast")
            st.metric(label="Price", value=P_CIVIC, label_visibility="collapsed")
            st.caption("For: **Political Activism**, Petitions, Community Organizing.")

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