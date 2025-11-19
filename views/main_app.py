# ... (Keep all imports at the top)
import payment_engine # <--- NEW IMPORT

# ... (Keep all init logic and config)

# ... (Inside show_main_app function) ...

    # ==================================================
    #  STATE 3: PAYMENT & FINALIZING
    # ==================================================
    elif st.session_state.app_mode == "finalizing":
        st.divider()
        st.subheader("💰 Checkout")

        # 1. Calculate Price
        price = 5.00 if is_heirloom else 2.50
        if st.session_state.overage_agreed:
            price += 1.00
            st.warning("Includes +$1.00 Overage Fee")
            
        st.markdown(f"**Total: ${price:.2f}**")

        # 2. Generate Payment Link
        if st.button(f"💳 Pay ${price:.2f} with Stripe"):
            # Generate a link that sends them to Stripe
            # For the prototype, we send them to Google.com as success/cancel just to test the flow
            # In production, this would be your actual app URL
            checkout_url = payment_engine.create_checkout_session(
                product_name=f"VerbaPost {service_tier}",
                amount_in_cents=int(price * 100),
                success_url="https://verbapost.com/success", # Placeholder
                cancel_url="https://verbapost.com/cancel"    # Placeholder
            )
            
            if "Error" in checkout_url:
                st.error(checkout_url)
            else:
                # Open Stripe in new tab
                st.link_button("👉 Click here to Complete Payment", checkout_url)
                st.info("After paying, return to this tab and click 'Confirm Payment' below.")

        st.divider()

        # 3. Finalize (The "I Paid" Button)
        # In a real app, we would use Webhooks to auto-verify. 
        # For Day 3 MVP, we trust the button (or check manually).
        if st.button("✅ I Have Paid - Send Letter", type="primary"):
            
            with st.status("✉️ Printing Letter...", expanded=True):
                full_recipient = f"{to_name}\n{to_street}\n{to_city}, {to_state} {to_zip}"
                full_return = f"{from_name}\n{from_street}\n{from_city}, {from_state} {from_zip}" if from_name else ""

                sig_path = None
                if canvas_result.image_data is not None:
                    img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                    sig_path = "temp_signature.png"
                    img.save(sig_path)

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
                     # mailer.send_letter(pdf_path)
                
                st.write("✅ Done!")

            st.balloons()
            st.success("Letter Generated Successfully!")
            
            # (Download button logic remains here...)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button("📄 Download PDF", pdf_file, "letter.pdf", "application/pdf")
            
            if st.button("Start New"):
                reset_app()