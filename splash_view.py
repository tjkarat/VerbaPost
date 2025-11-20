import streamlit as st

def show_splash():
    # --- HERO ---
    st.title("VerbaPost 📮")
    st.subheader("The Authenticity Engine.")
    st.markdown("##### Texts are trivial. Emails are ignored. Real letters get read.")
    
    st.divider()

    # --- HOW IT WORKS ---
    st.subheader("How it Works")
    step1, step2, step3 = st.columns(3)
    
    with step1:
        st.markdown("### 🎙️ 1. Dictate")
        st.write("Tap the mic and speak. AI handles the typing.")
    with step2:
        st.markdown("### ✍️ 2. Sign")
        st.write("Sign your name on screen.")
    with step3:
        st.markdown("### 📮 3. We Mail")
        st.write("We print, stamp, and mail it for you.")

    st.divider()

    # --- PRICING TIERS (The Fix: Using Metrics) ---
    st.subheader("Simple Pricing")
    
    # Custom CSS to center metrics
    st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        color: #E63946;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(label="⚡ Standard", value="$2.99", help="API Fulfillment • Window Envelope")
        st.caption("Mailed in 24hrs via automated center.")

    with c2:
        st.metric(label="🏺 Heirloom", value="$5.99", help="Hand-Stamped • Premium Paper")
        st.caption("Hand-prepared & mailed from Nashville, TN.")

    with c3:
        st.metric(label="🏛️ Civic Blast", value="$6.99", help="Mails 2 Senators + 1 Rep")
        st.caption("Activism Mode. Auto-finds your reps.")

    st.divider()

    # --- CTA ---
    col_spacer, col_btn, col_spacer2 = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🚀 Start Writing Now", type="primary", use_container_width=True):
            st.session_state.current_view = "main_app"
            st.rerun()

    st.markdown("<div style='text-align: center; margin-top: 20px;'><a href='#'>Log In</a></div>", unsafe_allow_html=True)