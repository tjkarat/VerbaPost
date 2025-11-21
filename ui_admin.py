import streamlit as st
import database
import letter_format
import os

# --- SECURITY CONFIG ---
# REPLACE THIS WITH YOUR EXACT LOGIN EMAIL
ADMIN_EMAIL = "tjkarat@gmail.com" 

def show_admin():
    st.title("👮‍♂️ Admin Command")
    
    # 1. Security Check
    if not st.session_state.get("user") or st.session_state.user_email != ADMIN_EMAIL:
        st.error("⛔ Access Denied.")
        if st.button("Back"):
            st.session_state.current_view = "splash"
            st.rerun()
        st.stop()

    # 2. Fetch Data
    queue = database.get_admin_queue()
    
    st.metric("Letters to Print", len(queue))
    st.divider()

    if not queue:
        st.success("All caught up! No pending orders.")
        return

    # 3. Render List
    for l in queue:
        with st.expander(f"📝 To: {l.recipient_name} ({l.created_at.strftime('%Y-%m-%d')})"):
            c1, c2 = st.columns([3, 1])
            
            with c1:
                st.markdown(f"**From:** {l.author.email}")
                st.markdown(f"**Address:** {l.recipient_street}, {l.recipient_city}, {l.recipient_state}")
                st.text_area("Content", l.content, height=100, disabled=True, key=f"txt_{l.id}")

            with c2:
                # RE-GENERATE PDF FOR PRINTING
                # Note: We pass None for signature as we don't store the image blob in SQL yet.
                # (Future improvement: Store sig in S3)
                
                # Rebuild Address Strings
                r_str = f"{l.recipient_name}\n{l.recipient_street}\n{l.recipient_city}, {l.recipient_state} {l.recipient_zip}"
                
                # Try to get sender string safely
                s_str = "VerbaPost User"
                if l.author:
                     s_str = f"{l.author.address_name}\n{l.author.address_street}\n{l.author.address_city}, {l.author.address_state} {l.author.address_zip}"

                pdf_path = letter_format.create_pdf(
                    l.content, r_str, s_str, True, "English", f"admin_{l.id}.pdf", None
                )
                
                with open(pdf_path, "rb") as f:
                    st.download_button("🖨️ Download PDF", f, file_name=f"Order_{l.id}.pdf", key=f"dl_{l.id}")
                
                st.write("")
                
                if st.button("✅ Mark Sent", key=f"btn_{l.id}"):
                    database.update_letter_status(l.id, "Sent")
                    st.toast("Marked as Sent!")
                    st.rerun()
