import streamlit as st
from audio_recorder_streamlit import audio_recorder
from streamlit_drawable_canvas import st_canvas
import ai_engine
import database
import letter_format
import mailer
import os
from PIL import Image
from datetime import datetime
import zipcodes

# --- CONFIG ---
st.set_page_config(page_title="VerbaPost", page_icon="📮")

# --- SESSION STATE ---
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "recording" 
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""

# --- IMPORTS ---
try:
    import recorder
    local_rec_available = True
except (ImportError, OSError):
    local_rec_available = False

# --- HELPERS ---
def validate_zip(zipcode, state):
    if not zipcodes.is_real(zipcode): return False, "Invalid Zip"
    details = zipcodes.matching(zipcode)
    if details and details[0]['state'] != state.upper():
         return False, f"Zip is in {details[0]['state']}"
    return True, "Valid"

def reset_app():
    st.session_state.app_mode = "recording"
    st.session_state.audio_path = None
    st.session_state.transcribed_text = ""
    st.rerun()

st.title("VerbaPost 📮")

# --- 1. ADDRESSING ---
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
    st.warning("👇 Fill out the **Recipient** tab to continue.")
    st.stop()

# --- 2. SETTINGS ---
st.divider()
service_tier = st.radio("Service Level:", ["⚡ Standard ($2.50)", "🏺 Heirloom ($5.00)"])
is_heirloom = "Heirloom" in service_tier

st.write("Sign Below:")
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)", 
    stroke_width=2, stroke_color="#000", background_color="#fff",
    height=100, width=300, drawing_mode="freedraw", key="sig"
)

# ==================================================
#  STATE MACHINE
# ==================================================
st.divider()
st.subheader("🎙️ Dictate Message")

# === STATE: RECORDING ===
if st.session_state.app_mode == "recording":
    st.info("Tap to START. Tap again to STOP.")
    
    audio_bytes = audio_recorder(
        text="",
        recording_color="#ff4b4b",
        neutral_color="#6aa36f",
        icon_size="80px",
        pause_threshold=60.0
    )
    
    if audio_bytes and len(audio_bytes) > 500:
        path = "temp_browser_recording.wav"
        with open(path, "wb") as f:
            f.write(audio_bytes)
        st.session_state.audio_path = path
        st.session_state.app_mode = "review_audio"
        st.rerun()

# === STATE: REVIEW AUDIO ===
elif st.session_state.app_mode == "review_audio":
    st.success("✅ Audio Captured")
    st.audio(st.session_state.audio_path)
    
    c1, c2 = st.columns(2)
    if c1.button("🔄 Re-Record"):
        reset_app()
    
    if c2.button("📝 Transcribe & Edit", type="primary"):
        with st.spinner("Transcribing..."):
            try:
                text = ai_engine.transcribe_audio(st.session_state.audio_path)
                st.session_state.transcribed_text = text
                st.session_state.app_mode = "review_text"
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# === STATE: EDIT TEXT (The New Feature) ===
elif st.session_state.app_mode == "review_text":
    st.info("✍️ Edit your letter below before finalizing.")
    
    # The User edits the text here
    edited_text = st.text_area("Letter Content:", value=st.session_state.transcribed_text, height=200)
    
    if st.button("🚀 Finalize & Generate PDF", type="primary"):
        st.session_state.transcribed_text = edited_text # Save edits
        st.session_state.app_mode = "finalizing"
        st.rerun()

# === STATE: FINALIZING ===
elif st.session_state.app_mode == "finalizing":
    with st.status("✉️ Printing...", expanded=True):
        full_recipient = f"{to_name}\n{to_street}\n{to_city}, {to_state} {to_zip}"
        full_return = f"{from_name}\n{from_street}\n{from_city}, {from_state} {from_zip}" if from_name else ""

        # Save Signature
        sig_path = None
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            sig_path = "temp_signature.png"
            img.save(sig_path)

        # Create PDF with the EDITED text
        pdf_path = letter_format.create_pdf(
            st.session_state.transcribed_text, 
            full_recipient, 
            full_return, 
            is_heirloom, 
            "final_letter.pdf", 
            sig_path
        )
        
        if not is_heirloom:
            st.write("🚀 Sending to API...")
            mailer.send_letter(pdf_path)
            
        st.write("✅ Done!")

    st.balloons()
    st.success("Letter Created!")
    
    safe_name = "".join(x for x in to_name if x.isalnum())
    unique_name = f"Letter_{safe_name}_{datetime.now().strftime('%H%M')}.pdf"

    with open(pdf_path, "rb") as pdf_file:
        st.download_button("📄 Download PDF", pdf_file, unique_name, "application/pdf", use_container_width=True)
    
    if st.button("Start New Letter"):
        reset_app()