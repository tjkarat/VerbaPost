import streamlit as st

def show_splash():
    st.title("VerbaPost 📮")
    st.subheader("The Authenticity Engine.")
    st.markdown(
        """
        **Don't just send a text. Send a legacy.**
        
        VerbaPost turns your spoken voice into a physical, mailed letter. 
        """
    )
    
    st.divider()

    # --- Feature Breakdown (Columns) ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### ⚡ Standard")
        st.caption("**.50 / letter**")
        st.write("API Fulfillment")
        st.write("Window Envelope")
        st.write("Mailed in 24hrs")

    with c2:
        st.markdown("### 🏺 Heirloom")
        st.caption("**.00 / letter**")
        st.write("Hand-stamped")
        st.write("Premium Paper")
        st.write("Mailed from Nashville, TN") # <--- FIXED

    with c3:
        st.markdown("### 🏛️ Civic")
        st.caption("**.00 / blast**")
        st.write("Mail your Senators")
        st.write("Auto-lookup")
        st.write("(Coming Soon)")

    st.divider()

    # --- Call to Action ---
    if st.button("🚀 Start Writing Now", type="primary", use_container_width=True):
        st.session_state.current_view = "main_app"
        st.rerun()

    st.markdown("Already a member? [Log In](#)")
