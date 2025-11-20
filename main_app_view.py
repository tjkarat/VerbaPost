import streamlit as st
from streamlit_drawable_canvas import st_canvas
import os
from PIL import Image
from datetime import datetime
import urllib.parse
import io
import zipfile # <--- NEW FOR BUNDLING

# Import core logic
import ai_engine
import database
import letter_format
import mailer
import zipcodes
import payment_engine
import civic_engine # <--- NEW ENGINE

# --- CONFIGURATION ---
MAX_BYTES_THRESHOLD = 35 * 1024 * 1024 
YOUR_APP_URL = "https://verbapost.streamlit.app" 

# --- PRICING ---
COST_STANDARD = 2.99
COST_HEIRLOOM = 5.99
COST_CIVIC = 6.99
COST_OVERAGE = 1.00

def validate_zip(zipcode, state):
    if not zipcodes.is_real(zipcode): return False, "Invalid Zip Code"
    details = zipcodes.matching(zipcode)
    if details and details[0]['state'] != state.upper():
         return False, f"Zip is in {details[0]['state']}, not {state}"
    return True, "Valid"

def reset_app():
    st.session_state.audio_path = None
    st.session_state.transcribed_text = ""
    st.session_state.app_mode = "recording"
    st.session_state.overage_agreed = False
    st.session_state.payment_complete = False
    st.query_params.clear()
    if "stripe_url" in st.session_state:
        del st.session_state.stripe_url
    if "last_config" in st.session_state:
        del st.session_state.last_config
    st.rerun()

def show_main_app():
    # --- 0. AUTO-DETECT RETURN FROM STRIPE ---
    if "session_id" in st.query_params:
        session_id = st.query_params["session_id"]
        if payment_engine.check_payment_status(session_id):
            st.session_state.payment_complete = True
            st.toast("✅ Payment Confirmed! Recorder Unlocked.")
            st.query_params.clear() 
        else:
            st.error("Payment verification failed.")

    # --- INIT STATE ---
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "recording"
    if "audio_path" not in st.session_state:
        st.session_state.audio_path = None
    if "transcribed_text" not in st.session_state:
        st.session_state.transcribed_text = ""
    if "overage_agreed" not in st.session_state:
        st.session_state.overage_agreed = False
    if "payment_complete" not in st.session_state:
        st.session_state.payment_complete = False
    
    # --- SIDEBAR RESET ---
    with st.sidebar:
        st.subheader("Controls")
        if st.button("🔄 Start New Letter", type="primary", use_container_width=True):
            reset_app()
    
    # --- 1. ADDRESSING ---
    st.subheader("1. Addressing")
    col_to, col_from = st.tabs(["👉 Recipient", "👈 Sender"])

    def get_val(key): return st.session_state.get(key, st.query_params.get(key, ""))

    with col_to:
        # Disable Recipient input if Civic Mode is active (we find them auto)
        # For now, we keep it open but ignore it in Civic logic
        to_name = st.text_input("Recipient Name", value=get_val("to_name"), key="to_name", placeholder="Ignored for Civic Mode")
        to_street = st.text_input("Street Address", value=get_val("to_street"), key="to_street")
        c1, c2 = st.columns(2)
        to_city = c1.text_input("City", value=get_val("to_city"), key="to_city")
        to_state = c2.text_input("State", value=get_val("to_state"), max_chars=2, key="to_state")
        to_zip = c2.text_input("Zip", value=get_val("to_zip"), max_chars=5, key="to_zip")

    with col_from:
        from_name = st.text_input("Your Name", value=get_val("from_name"), key="from_name")
        from_street = st.text_input("Your Street", value=get_val("from_street"), key="from_street")
        from_city = st.text_input("Your City", value=get_val("from_city"), key="from_city")
        c3, c4 = st.columns(2)
        from_state = c3.text_input("Your State", value=get_val("from_state"), max_chars=2, key="from_state")
        from_zip = c4.text_input("Your Zip", value=get_val("from_zip"), max_chars=5, key="from_zip")

    # Logic: For Civic mode, we only need SENDER address to look up reps.
    # For others, we need both.
    
    # --- 2. SETTINGS ---
    st.divider()
    c_set, c_sig = st.columns(2)
    with c_set:
        st.subheader("2. Settings")
        service_tier = st.radio("Service Level:", 
            [f"⚡ Standard (${COST_STANDARD})", f"🏺 Heirloom (${COST_HEIRLOOM})", f"🏛️ Civic (${COST_CIVIC})"],
            key="tier_select"
        )
        is_heirloom = "Heirloom" in service_tier
        is_civic = "Civic" in service_tier
    with c_sig:
        st.subheader("3. Sign")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)", stroke_width=2, stroke_color="#000", background_color="#fff",
            height=100, width=200, drawing_mode="freedraw", key="sig"
        )

    # Validation Logic
    if not is_civic:
        if not (to_name and to_street and to_city and to_state and to_zip):
            st.info("👇 Fill out Recipient to unlock.")
            return
    else:
        # For Civic, we need Sender address to find reps
        if not (from_street and from_city and from_state and from_zip):
            st.info("👇 Fill out **Sender** address to find your Representatives.")
            return

    st.divider()
    
    # --- PAYMENT ---
    if is_heirloom: price = COST_HEIRLOOM
    elif is_civic: price = COST_CIVIC
    else: price = COST_STANDARD
    final_price = price + (COST_OVERAGE if st.session_state.overage_agreed else 0.00)

    if not st.session_state.payment_complete:
        st.subheader("4. Payment")
        st.info(f"Total: **${final_price:.2f}**")
        
        # URL Params persistence
        params = {
            "to_name": to_name, "to_street": to_street, "to_city": to_city, "to_state": to_state, "to_zip": to_zip,
            "from_name": from_name, "from_street": from_street, "from_city": from_city, "from_state": from_state, "from_zip": from_zip
        }
        query_string = urllib.parse.urlencode(params)
        success_link = f"{YOUR_APP_URL}?{query_string}"

        current_config = f"{service_tier}_{final_price}"
        if "stripe_url" not in st.session_state or st.session_state.get("last_config") != current_config:
             url, session_id = payment_engine.create_checkout_session(
                product_name=f"VerbaPost {service_tier}",
                amount_in_cents=int(final_price * 100),
                success_url=success_link, 
                cancel_url=YOUR_APP_URL
            )
             st.session_state.stripe_url = url
             st.session_state.stripe_session_id = session_id
             st.session_state.last_config = current_config
        
        if st.session_state.stripe_url:
            st.link_button(f"💳 Pay ${final_price:.2f} & Unlock Recorder", st.session_state.stripe_url, type="primary")
            st.caption("Secure checkout via Stripe.")
            if st.button("🔄 I've Paid (Refresh Status)"):
                 if payment_engine.check_payment_status(st.session_state.stripe_session_id):
                     st.session_state.payment_complete = True
                     st.rerun()
                 else:
                     st.error("Payment not found. Please pay first.")
        else:
            st.error("Connection Error. Please refresh.")
        st.stop() 

    # --- RECORDING ---
    if st.session_state.app_mode == "recording":
        st.subheader("🎙️ 5. Dictate")
        
        # Show who we are messaging if Civic
        if is_civic:
            st.info("🏛️ **Civic Mode Active:** This one voice note will be sent to your 2 Senators and 1 Representative.")
        
        audio_value = st.audio_input("Record your letter")
        if audio_value:
            with st.status("⚙️ Processing...", expanded=True):
                path = "temp_browser_recording.wav"
                with open(path, "wb") as f:
                    f.write(audio_value.getvalue())
                st.session_state.audio_path = path
                
                file_size = audio_value.getbuffer().nbytes
                if file_size > MAX_BYTES_THRESHOLD:
                    st.error("Recording too long.")
                    if st.button(f"💳 Agree to +${COST_OVERAGE}"):
                        st.session_state.overage_agreed = True
                        st.session_state.app_mode = "transcribing"
                        st.rerun()
                    if st.button("🗑️ Retry"):
                        st.session_state.audio_path = None
                        st.rerun()
                    st.stop()
                else:
                    st.session_state.app_mode = "transcribing"
                    st.rerun()

    # --- TRANSCRIPT ---
    elif st.session_state.app_mode == "transcribing":
        with st.spinner("🧠 AI is writing..."):
            try:
                text = ai_engine.transcribe_audio(st.session_state.audio_path)
                st.session_state.transcribed_text = text
                st.session_state.app_mode = "editing"
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
                if st.button("Retry"): reset_app()

    # --- EDITING ---
    elif st.session_state.app_mode == "editing":
        st.divider()
        st.subheader("📝 Review")
        st.audio(st.session_state.audio_path)
        edited_text = st.text_area("Edit Text:", value=st.session_state.transcribed_text, height=300)
        
        c1, c2 = st.columns([1, 3])
        if c1.button("✨ AI Polish"):
             st.session_state.transcribed_text = ai_engine.polish_text(edited_text)
             st.rerun()
        if c2.button("🗑️ Re-Record"):
             st.session_state.app_mode = "recording"
             st.rerun()

        st.markdown("---")
        if st.button("🚀 Approve & Send Now", type="primary", use_container_width=True):
            st.session_state.transcribed_text = edited_text
            st.session_state.app_mode = "finalizing"
            st.rerun()

    # --- FINALIZING (CIVIC BLAST LOGIC) ---
    elif st.session_state.app_mode == "finalizing":
        st.divider()
        with st.status("✉️ Processing...", expanded=True) as status:
            
            sig_path = None
            if canvas_result.image_data is not None:
                img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                sig_path = "temp_signature.png"
                img.save(sig_path)

            full_return_str = f"{from_name}\n{from_street}\n{from_city}, {from_state} {from_zip}"
            addr_from = {'name': from_name, 'street': from_street, 'city': from_city, 'state': from_state, 'zip': from_zip}
            lang = st.session_state.get("language", "English")

            final_files = [] # Store (filename, path) for zip

            if is_civic:
                st.write("🏛️ Finding your Representatives via Google API...")
                # Lookup logic
                full_user_address = f"{from_street}, {from_city}, {from_state} {from_zip}"
                targets = civic_engine.get_reps(full_user_address)
                
                if not targets:
                    st.error("Could not find representatives for this address. Generating generic letter instead.")
                    # Fallback list? Or just stop? 
                    # Let's stop to be safe, or generate one PDF to user.
                
                for i, target in enumerate(targets):
                    st.write(f"📄 Generating letter for {target['title']} {target['name']}...")
                    
                    # Create unique filename
                    fname = f"Letter_to_{target['name'].replace(' ', '')}.pdf"
                    
                    # Format Recipient String
                    t_addr = target['address_obj']
                    full_recipient_str = f"{target['name']}\n{t_addr['street']}\n{t_addr['city']}, {t_addr['state']} {t_addr['zip']}"
                    
                    # Generate PDF
                    pdf_path = letter_format.create_pdf(
                        st.session_state.transcribed_text, full_recipient_str, full_return_str, 
                        False, lang, fname, sig_path
                    )
                    final_files.append(pdf_path)
                    
                    # Send to Lob
                    st.write(f"🚀 Mailing to {target['name']}...")
                    mailer.send_letter(pdf_path, t_addr, addr_from)

            else:
                # STANDARD FLOW
                st.write("📄 Generating PDF...")
                full_recipient_str = f"{to_name}\n{to_street}\n{to_city}, {to_state} {to_zip}"
                pdf_path = letter_format.create_pdf(
                    st.session_state.transcribed_text, full_recipient_str, full_return_str, 
                    is_heirloom, lang, "final_letter.pdf", sig_path
                )
                final_files.append(pdf_path)
                
                if not is_heirloom:
                    addr_to = {'name': to_name, 'street': to_street, 'city': to_city, 'state': to_state, 'zip': to_zip}
                    st.write("🚀 Transmitting to Lob...")
                    mailer.send_letter(pdf_path, addr_to, addr_from)
            
            st.write("✅ Done!")
            status.update(label="Complete!", state="complete")

        st.balloons()
        st.success("All letters sent!")
        
        # --- DOWNLOAD LOGIC (ZIP OR PDF) ---
        if len(final_files) > 1:
            # ZIP THEM UP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for file_path in final_files:
                    zf.write(file_path, os.path.basename(file_path))
            
            st.download_button(
                label="📦 Download All Letters (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="VerbaPost_Civic_Blast.zip",
                mime="application/zip",
                use_container_width=True
            )
        elif len(final_files) == 1:
            with open(final_files[0], "rb") as f:
                st.download_button("📄 Download Copy", f, "letter.pdf", use_container_width=True)

        if st.button("Start New"):
            reset_app()