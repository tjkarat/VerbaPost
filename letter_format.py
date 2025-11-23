from fpdf import FPDF
import os
import requests
from datetime import datetime

# Font URLs
CAVEAT_URL = "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat-Regular.ttf"
CJK_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

def ensure_fonts():
    """Downloads Caveat font if missing."""
    if not os.path.exists("Caveat-Regular.ttf"):
        try:
            print("⬇️ Downloading Caveat Font...")
            r = requests.get(CAVEAT_URL, allow_redirects=True)
            with open("Caveat-Regular.ttf", "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"Font Download Error: {e}")

def create_pdf(content, recipient_addr, return_addr, is_heirloom, language, filename="letter.pdf", signature_path=None):
    ensure_fonts()
    
    pdf = FPDF()
    pdf.add_page()
    
    # --- FONT SELECTION ---
    font_family = 'Helvetica' # Fallback
    
    if language == "English":
        if os.path.exists("Caveat-Regular.ttf"):
            pdf.add_font('Caveat', '', "Caveat-Regular.ttf", uni=True)
            font_family = 'Caveat'
            body_size = 16 # Handwriting needs to be bigger
        else:
            font_family = 'Helvetica'
            body_size = 12
            
    elif language in ["Japanese", "Chinese", "Korean"]:
        if os.path.exists(CJK_PATH):
            try:
                pdf.add_font('NotoCJK', '', CJK_PATH, uni=True)
                font_family = 'NotoCJK'
                body_size = 12
            except: pass
    else:
        body_size = 12

    # --- LAYOUT ---
    
    # 1. Return Address
    # Use standard font for address to ensure postal readability
    pdf.set_font('Helvetica', '', 10) 
    pdf.set_xy(10, 10)
    pdf.multi_cell(0, 5, return_addr)
    
    # 2. Recipient Address
    pdf.set_xy(20, 40)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.multi_cell(0, 6, recipient_addr)
    
    # 3. Date
    pdf.set_xy(160, 10)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 10, datetime.now().strftime("%Y-%m-%d"), ln=True, align='R')
    
    # 4. Body Content (Custom Font)
    pdf.set_xy(10, 80)
    pdf.set_font(font_family, '', body_size)
    pdf.multi_cell(0, 8, content)
    
    # 5. Signature
    if signature_path and os.path.exists(signature_path):
        pdf.ln(10)
        pdf.image(signature_path, w=40)
    
    # 6. Footer
    pdf.set_y(-20)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.cell(0, 10, 'Dictated via VerbaPost.com', 0, 0, 'C')

    # Save
    save_path = f"/tmp/{filename}"
    pdf.output(save_path)
    return save_path