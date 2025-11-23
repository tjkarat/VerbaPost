import streamlit as st
import database
import letter_format
import os
import pandas as pd

def show_admin():
    st.title("👮‍♂️ Admin Command")
    
    # 1. SECURITY: Load Admin Email from Secrets
    try:
        admin_email = st.secrets["admin"]["email"]
    except:
        st.error("❌ Admin Email not configured in Streamlit Secrets.")
        st.info("Go to Settings > Secrets and add [admin] email = 'your@email.com'")
        st.stop()
    
    # 2. Security Gate
    current_user_email = st.session_state.get("user_email") or ""
    if not st.session_state.get("user") or current_user_email.lower() != admin_email.lower():
        st.error("⛔ Access Denied. Authorized Personnel Only.")
        if st.button("Back to Safety"):
            st.session_state.current_view = "splash"
            st.rerun()
        st.stop()

    # 3. Fetch Data
    try:
        queue = database.get_admin_queue()
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return

    # 4. Business Stats
    col1, col2, col3 = st.columns(3)
    
    pending_count = len(queue)
    estimated_value = pending_count * 5.99 
    
    col1.metric("Pending Orders", pending_count, delta_color="inverse")
    col2.metric("Queue Value", f"${estimated_value:.2f}")
    col3.button("🔄 Refresh", on_click=st.rerun)

    st.divider()
    st.subheader("🗂️ Fulfillment Queue")

    if not queue:
        st.success("🎉 All caught up! No pending orders.")
        st.balloons()
        return

    # 5. The Work List
    for l in queue:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            
            with c1:
                st.markdown(f"**To:** {l.recipient_name}")
                st.caption(f"📍 {l.recipient_street}, {l.recipient_city}, {l.recipient_state} {l.recipient_zip}")
                st.text(f"Message Preview: {l.content[:75]}...")
                st.caption(f"Ordered: {l.created_at.strftime('%b %d, %I:%M %p')}")

            with c2:
                # GENERATE PDF
                s_name = l.author.address_name if l.author else "VerbaPost User"
                s_addr = f"{l.author.address_street}\n{l.author.address_city}, {l.author.address_state}" if l.author else ""
                
                s_str = f"{s_name}\n{s_addr}"
                r_str = f"{l.recipient_name}\n{l.recipient_street}\n{l.recipient_city}, {l.recipient_state} {l.recipient_zip}"
                
                # Generate filename
                pdf_path = letter_format.create_pdf(
                    l.content, r_str, s_str, True, "English", f"order_{l.id}.pdf", None
                )
                
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "🖨️ Print PDF", 
                        data=f, 
                        file_name=f"VerbaPost_Order_{l.id}.pdf", 
                        mime="application/pdf",
                        key=f"dl_{l.id}"
                    )
                
                # MARK AS SENT
                if st.button("✅ Mark Mailed", key=f"sent_{l.id}", type="primary"):
                    database.update_letter_status(l.id, "Sent")
                    st.toast(f"Order #{l.id} Archived!")
                    st.rerun()
