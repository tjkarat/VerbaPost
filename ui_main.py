import streamlit as st
from streamlit_drawable_canvas import st_canvas
import os
from PIL import Image
from datetime import datetime
import urllib.parse
import io
import zipfile

# Import core logic
import ai_engine 
import database
import letter_format
import mailer
import zipcodes
import payment_engine
import civic_engine

# --- CONFIG ---
YOUR_APP_URL = "https://verbapost.streamlit.app" 
COST_STANDARD = 2.99
COST_HEIRLOOM = 5.99
COST_CIVIC = 6.99
COST_OVERAGE = 1.00

def reset_app():
    # Clear session but keep login
    keys = ["audio_path", "transcribed_text", "overage_agreed", "payment_complete", "stripe_url", "processed_ids", "locked_tier"]
    for k in keys:
        if k in st.session_state: del st.session_state[k]
    
    # Clear address fields from session
    addr_keys = ["to_name", "to_street", "to_city", "to_state", "to_zip", "from_name", "from_street", "from_city", "from_state", "from_zip"]
    for k in addr_keys:
        if k in st.session_state: del st.session_state[k]
        
    st.query_params.clear()
    st.rerun()

def show_main_app():
    # --- 0. URL HYDRATION (Runs First) ---
    qp = st.query_params
    if "session_id" in qp:
        session_id = qp["session_id"]
        # Verify Payment if not already done
        if session_id not in st.session_state.get("processed_ids", []):
            if payment_engine.check_payment_status(session_id):
                st.session_state.payment_complete = True
                if "processed_ids" not in st.session_state: st.session_state.processed_ids = []
                st.session_state.processed_ids.append(session_id)
                st.toast("✅ Payment Verified! Welcome back.")
            
            # Restore Address from URL to Session State
            keys = ["to_name", "to_street", "to_city", "to_state", "to_zip", 
                    "from_name", "from_street", "from_city", "from_state", "from_zip"]
            for k in keys:
                if k in qp: st.session_state[k] = qp[k]
            
            # Restore Tier
            if "tier" in qp: st.session_state.locked_tier = qp["tier"]

            # Force Recording Mode
            st.session_state.app_mode = "recording"
            
            # Clear URL to look clean (but data is now in Session State)
            st.query_params.clear()

    # --- INIT DEFAULTS ---
    if "app_mode" not in st.session_state: st.session_state.app_mode = "recording"
    if "payment_complete" not in st.session_state: st.session_state.payment_complete = False

    # --- SIDEBAR ---
    with st.sidebar:
        st.subheader("Controls")
        if st.button("🔄 Start New Letter", type="primary"): reset_app()

    # ==========================================
    #  SECTION 1: INPUTS (ALWAYS RENDERED)
    # ==========================================
    st.subheader("1. Addressing")
    col_to, col_from = st.tabs(["👉 Recipient", "👈 Sender"])

    # Data Binding: Priority is Session State -> Empty
    def get(k): return st.session_state.get(k, "")

    with col_to:
        to_name = st.text_input("Recipient Name", value=get("to_name"), key="to_name")
        to_street = st.text_input("Street Address", value=get("to_street"), key="to_street")
        c1, c2 = st.columns(2)
        to_city = c1.text_input("City", value=get("to_city"), key="to_city")
        to_state = c2.text_input("State", value=get("to_state"), max_chars=2, key="to_state")
        to_zip = c2.text_input("Zip", value=get("to_zip"), max_chars=5, key="to_zip")

    with col_from:
        from_name = st.text_input("Your Name", value=get("from_name"), key="from_name")
        from_street = st.text_input("Your Street", value=get("from_street"), key="from_street")
        from_city = st.text_input("Your City", value=get("from_city"), key="from_city")
        c3, c4 = st.columns(2)
        from_state = c3.text_input("Your State", value=get("from_state"), max_chars=2, key="from_state")
        from_zip = c4.text_input("Your Zip", value=get("from_zip"), max_chars=5, key="from_zip")

    # Service Tier Logic
    if st.session_state.payment_complete:
        service_tier = st.session_state.get("locked_tier", "Standard")
        st.success(f"✅ Order Active: **{service_tier}**")
    else:
        st.divider()
        st.subheader("2. Service")
        service_tier = st.radio("Choose Tier:", 
            [f"⚡ Standard (${COST_STANDARD})", f"🏺 Heirloom (${COST_HEIRLOOM})", f"🏛️ Civic (${COST_CIVIC})"],
            key="tier_select"
        )

    is_heirloom = "Heirloom" in service_tier
    is_civic = "Civic" in service_tier

    # Validation Check
    valid_sender = from_name and from_street and from_city and from_state and from_zip
    valid_recipient = to_name and to_street and to_city and to_state and to_zip

    if is_civic:
        if not valid_sender:
            st.warning("⚠️ Please fill out the **Sender** tab.")
            st.stop()
    else:
        if not (valid_recipient and valid_sender):
            st.info("👇 Please fill out **Recipient** and **Sender** tabs.")
            st.stop()

    # Signature (ALWAYS Rendered so variable exists)
    st.divider()
    st.subheader("3. Sign")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)", stroke_width=2, stroke_color="#000", background_color="#fff",
        height=200, width=350, drawing_mode="freedraw", key="sig"
    )

    # ==========================================
    #  SECTION 2: PAYMENT GATE (BLOCKS HERE)
    # ==========================================
    if is_heirloom: price = COST_HEIRLOOM
    elif is_civic: price = COST_CIVIC
    else: price = COST_STANDARD
    
    final_price = price + (COST_OVERAGE if st.session_state.get("overage_agreed", False) else 0.00)

    if not st.session_state.payment_complete:
        st.divider()
        st.subheader("4. Payment")
        st.info(f"Total: **${final_price:.2f}**")
        
        # Save Draft & Generate Link
        user_email = st.session_state.get("user_email", "guest@verbapost.com")
        
        if st.button("💳 Proceed to Secure Payment", type="primary", use_container_width=True):
            draft_id = database.save_draft(user_email, to_name, to_street, to_city, to_state, to_zip)
            
            if draft_id:
                # Pack data into URL for return trip
                params = {
                    "to_name": to_name, "to_street": to_street, "to_city": to_city, "to_state": to_state, "to_zip": to_zip,
                    "from_name": from_name, "from_street": from_street, "from_city": from_city, "from_state": from_state, "from_zip": from_zip,
                    "tier": service_tier,
                    "letter_id": draft_id
                }
                q_str = urllib.parse.urlencode(params)
                success_url = f"{YOUR_APP_URL}?{q_str}"
                
                url, sess_id = payment_engine.create_checkout_session(
                    f"VerbaPost {service_tier}", int(final_price * 100), success_url, YOUR_APP_URL
                )
                
                if url:
                    st.link_button("👉 Click to Pay (Opens Secure Tab)", url, type="primary")
                    st.caption("After paying, you will be redirected back here to record your letter.")
                else:
                    st.error("Payment Error.")
        st.stop() # Stop execution if not paid

    # ==========================================
    #  SECTION 3: WORKSPACE (UNLOCKED)
    # ==========================================
    st.divider()
    
    if st.session_state.app_mode == "recording":
        st.subheader("🎙️ 5. Dictate")
        st.markdown("""
        <div style="background-color:#e8fdf5; padding:15px; border-radius:10px; border:1px solid #c3e6cb; margin-bottom:10px;">
            <h4 style="margin-top:0; color:#155724;">👇 How to Record</h4>
            <ol style="color:#155724; margin-bottom:0;">
                <li>Tap the <b>Microphone Icon</b> below.</li>
                <li>Speak your letter clearly.</li>
                <li>Tap the <b>Red Square</b> to stop.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        audio_val = st.audio_input("Record")
        if audio_val:
            with st.status("Processing...", expanded=True):
                path = "temp.wav"
                with open(path, "wb") as f: f.write(audio_val.getvalue())
                st.session_state.audio_path = path
                st.session_state.app_mode = "transcribing"
                st.rerun()

    elif st.session_state.app_mode == "transcribing":
        with st.spinner("Transcribing..."):
            try:
                text = ai_engine.transcribe_audio(st.session_state.audio_path)
                st.session_state.transcribed_text = text
                st.session_state.app_mode = "editing"
                st.rerun()
            except:
                st.error("Transcription Error")
                if st.button("Retry"): reset_app()

    elif st.session_state.app_mode == "editing":
        st.subheader("📝 Review")
        edited = st.text_area("Body:", value=st.session_state.transcribed_text, height=300)
        if st.button("🚀 Send Letter", type="primary"):
            st.session_state.transcribed_text = edited
            st.session_state.app_mode = "finalizing"
            st.rerun()

    elif st.session_state.app_mode == "finalizing":
        with st.status("Sending...", expanded=True):
            sig_path = None
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                sig_path = "temp_signature.png"
                img.save(sig_path)

            # Civic vs Standard Logic
            if is_civic:
                full_addr = f"{from_street}, {from_city}, {from_state} {from_zip}"
                try: targets = civic_engine.get_reps(full_addr)
                except: targets = []
                
                if not targets:
                    st.error("No Reps found.")
                    st.stop()
                
                files = []
                addr_from = {'name': from_name, 'street': from_street, 'city': from_city, 'state': from_state, 'zip': from_zip}
                for t in targets:
                    t_addr = t['address_obj']
                    pdf = letter_format.create_pdf(st.session_state.transcribed_text, f"{t['name']}\n{t_addr['street']}", f"{from_name}\n{from_street}...", False, "English", f"{t['name']}.pdf", sig_path)
                    files.append(pdf)
                    t_lob = {'name': t['name'], 'street': t_addr['street'], 'city': t_addr['city'], 'state': t_addr['state'], 'zip': t_addr['zip']}
                    mailer.send_letter(pdf, t_lob, addr_from)
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for f in files: zf.write(f, os.path.basename(f))
                st.download_button("📦 Download All", zip_buffer.getvalue(), "Civic.zip")
            
            else:
                # Standard
                pdf = letter_format.create_pdf(
                    st.session_state.transcribed_text, 
                    f"{to_name}\n{to_street}", 
                    f"{from_name}\n{from_street}", 
                    is_heirloom, "English", "final.pdf", sig_path
                )
                
                if not is_heirloom:
                     addr_to = {'name': to_name, 'street': to_street, 'city': to_city, 'state': to_state, 'zip': to_zip}
                     addr_from = {'name': from_name, 'street': from_street, 'city': from_city, 'state': from_state, 'zip': from_zip}
                     mailer.send_letter(pdf, addr_to, addr_from)
                else:
                     # Update status for Admin
                     if "letter_id" in st.query_params:
                         database.update_letter_status(st.query_params["letter_id"], "Queued", st.session_state.transcribed_text)

                with open(pdf, "rb") as f:
                    st.download_button("Download Copy", f, "letter.pdf")

            st.write("✅ Done!")
            st.success("Sent!")
            
            # Save Address
            if st.session_state.get("user"):
                 database.update_user_address(st.session_state.user.user.email, from_name, from_street, from_city, from_state, from_zip)

        if st.button("Start New"): reset_app()