import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_drawable_canvas import st_canvas
import os
from PIL import Image
from datetime import datetime

# Import core logic modules
import ai_engine
import database
import letter_format
import mailer
import zipcodes

# --- CONFIGURATION ---
MAX_RECORDING_TIME = 180
ENERGY_THRESHOLD = 400
PAUSE_THRESHOLD = 60.0

def validate_zip(zipcode, state):
    if not zipcodes.is_real(zipcode): return False, "Invalid Zip Code"
    details = zipcodes.matching(zipcode)
    if details and details[0]['state'] != state.upper():
         return False, f"Zip is in {details[0]['state']}, not {state}"
    return True, "Valid"

def reset_recording_state():
    st.session_state.audio_path = None
    st.session_state.transcribed_text = ""
    st.rerun()

def show_main_app():
    """
    The Core Application Logic.
    """
    # --- 0. INIT SESSION STATE (The Fix) ---
    # This ensures the variables exist before we try to use them
    if "audio_path" not in st.session_state:
        st.session_state.audio_path = None
    if "transcribed_text" not in st.session_state:
        st.session_state.transcribed_text = ""
    
    # --- 1. ADDRESSING SECTION ---
    st.subheader("1. Addressing")
    col_to, col_from = st.tabs(["👉 Recipient", "👈 Sender"])

    with col_to:
        to_name = st.text_input("Recipient Name", placeholder="John Doe")
        to_street = st.text_input("Street Address", placeholder="123 Main St")
        c1, c2 = st.columns(2)
        to_city = c1.text_input("City", placeholder="Mt Juliet")
        to_state = c2.text_input("State", max_chars=2, placeholder="TN")
        to_zip = c2.text_input("Zip", max_chars=5, placeholder="37122")

    with col_from:
        from_name = st.text_input("Your Name")
        from_street = st.text_input("Your Street")
        from_city = st.text_input("Your City")
        c3, c4 = st.columns(2)
        from_state = c3.text_input("Your State", max_chars=2)
        from_zip = c4.text_input("Your Zip", max_chars=5)

    if not (to_name and to_street and to_city and to_state and to_zip):
        st.info("👇 Fill out the **Recipient** tab to unlock the tools.")
        return

    # --- 2. SETTINGS & SIGNATURE ---
    st.divider()
    c_set, c_sig = st.columns(2)
    
    with c_set:
        st.subheader("Settings")
        service_tier = st.radio("Tier:", ["⚡ Standard ($2.50)", "🏺 Heirloom ($5.00)", "🏛️ Civic ($6.00)"])
        is_heirloom = "Heirloom" in service_tier

    with c_sig:
        st.subheader("Sign")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2, stroke_color="#000", background_color="#fff",
            height=100, width=200, drawing_mode="freedraw", key="sig"
        )

    # --- 3. RECORDING ---
    st.divider()
    st.subheader("🎙️ Dictate")
    
    audio_bytes = audio_recorder(
        text="",
        recording_color="#ff4b4b",
        neutral_color="#6aa36f",
        icon_size="80px",
        pause_threshold=PAUSE_THRESHOLD, 
        energy_threshold=ENERGY_THRESHOLD
    )

    if audio_bytes:
        if len(audio_bytes) > 2000: 
            path = "temp_browser_recording.wav"
            with open(path, "wb") as f:
                f.write(audio_bytes)
            st.session_state.audio_path = path
            st.success(f"✅ Audio Captured! Ready to Transcribe.")
            
    # --- 4. GENERATE & SEND ---
    if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
        
        if st.button("🚀 Generate & Mail Letter", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                # A. Transcribe
                try:
                    text_content = ai_engine.transcribe_audio(st.session_state.audio_path)
                except Exception as e:
                    st.error(f"Transcription Failed: {e}")
                    return

                # B. Save Signature Image
                sig_path = None
                if canvas_result.image_data is not None:
                    img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                    sig_path = "temp_signature.png"
                    img.save(sig_path)

                # C. Create PDF
                full_recipient = f"{to_name}\n{to_street}\n{to_city}, {to_state} {to_zip}"
                full_return = f"{from_name}\n{from_street}\n{from_city}, {from_state} {from_zip}" if from_name else ""
                
                pdf_path = letter_format.create_pdf(
                    text_content, full_recipient, full_return, is_heirloom, "final_letter.pdf", sig_path
                )
                
                # D. Final UI
                st.balloons()
                st.success("Generated Successfully!")
                st.text_area("Final Text:", value=text_content)
                
                if not is_heirloom:
                    mailer.send_letter(pdf_path)

                # Unique Filename logic
                safe_name = "".join(x for x in to_name if x.isalnum())
                unique_name = f"Letter_{safe_name}_{datetime.now().strftime('%H%M')}.pdf"

                with open(pdf_path, "rb") as pdf_file:
                    st.download_button("📄 Download PDF", pdf_file, unique_name, "application/pdf", use_container_width=True)

                if st.button("Start Over"):
                    reset_recording_state()