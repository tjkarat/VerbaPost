import streamlit as st

def show_splash():
    # --- CONFIG ---
    P_STANDARD = "$2.99"
    P_HEIRLOOM = "$5.99"
    P_CIVIC = "$6.99"

    # --- HERO ---
    st.title("VerbaPost 📮")
    st.subheader("The Authenticity Engine.")
    st.markdown("##### Texts are trivial. Emails are ignored. Real letters get read.")
    
    st.divider()

    # --- HOW IT WORKS (Updated Verbiage) ---
    st.subheader("How it Works")
    step1, step2, step3 = st.columns(3)
    
    with step1:
        st.markdown("### 🎙️ 1. Dictate")
        st.write("Tap the mic and speak naturally. Our AI transcribes, polishes, and prepares your message.")
    
    with step2:
        st.markdown("### ✍️ 2. Sign")
        st.write("Review the text, sign your name on the screen, and choose your style.")
    
    with step3:
        st.markdown("### 📮 3. We Mail")
        st.write("We print, stamp, and mail it for you.")

    st.divider()

    # --- PRICING TIERS (HTML GRID) ---
    st.subheader("Simple Pricing")
    
    html_pricing = """
    <style>
        .price-card {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #ddd;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .price-tag {
            color: #E63946;
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }
        .price-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .price-desc {
            font-size: 14px;
            color: #555;
            line-height: 1.4;
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
    </style>

    <div class="grid-container">
        <div class="price-card">
            <div>
                <div class="price-title">⚡ Standard</div>
                <div class="price-tag">&#36;2.99</div>
                <div class="price-desc">API Fulfillment<br>Window Envelope<br>Mailed in 24hrs</div>
            </div>
        </div>

        <div class="price-card" style="border: 2px solid #4CAF50; background-color: #f0fff4;">
            <div>
                <div class="price-title">🏺 Heirloom</div>
                <div class="price-tag">&#36;5.99</div>
                <div class="price-desc">Hand-Stamped<br>Premium Paper<br>Mailed from Nashville</div>
            </div>
        </div>

        <div class="price-card">
            <div>
                <div class="price-title">🏛️ Civic Blast</div>
                <div class="price-tag">&#36;6.99</div>
                <div class="price-desc">Activism Mode<br>Auto-Find Reps<br>Mails Senate + House</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html_pricing, unsafe_allow_html=True)

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