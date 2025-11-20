import stripe
import streamlit as st

# --- LOAD KEYS ---
try:
    stripe.api_key = st.secrets["stripe"]["secret_key"]
except Exception as e:
    pass

def create_checkout_session(product_name, amount_in_cents, success_url, cancel_url):
    """
    Creates a Stripe Checkout Session.
    Accepts explicit success_url and cancel_url arguments.
    """
    try:
        # Verify key exists
        if not stripe.api_key:
            return None, "Error: Stripe API Key is missing."

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product_name,
                    },
                    'unit_amount': amount_in_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            # Stripe appends session_id automatically to the success URL if configured here
            success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=cancel_url,
        )
        # Return Tuple: (URL, ID)
        return session.url, session.id
    except Exception as e:
        return None, str(e)

def check_payment_status(session_id):
    """
    Verifies a session ID with Stripe.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            return True
    except:
        pass
    return False