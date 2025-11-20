import streamlit as st
from supabase import create_client, Client
import database
import time

# --- LOAD SECRETS SAFELY ---
try:
    url = st.secrets.get("supabase", {}).get("url", "")
    key = st.secrets.get("supabase", {}).get("key", "")
    
    if url and key:
        supabase: Client = create_client(url, key)
        AUTH_ACTIVE = True
    else:
        supabase = None
        AUTH_ACTIVE = False
except Exception as e:
    supabase = None
    AUTH_ACTIVE = False
    print(f"Auth Init Error: {e}")

def get_supabase_client():
    if not AUTH_ACTIVE: 
        return None, "Missing [supabase] section in Secrets."
    return supabase, None

# --- NEW SIGNUP SIGNATURE (Includes Address Fields) ---
def sign_up(email, password, name, street, city, state, zip_code):
    client, err = get_supabase_client()
    if err: return None, err
    
    try:
        response = client.auth.sign_up({"email": email, "password": password})
        
        if response.user:
             # 2. Sync with Database and UPDATE ADDRESS
             database.create_or_get_user(email)
             database.update_user_address(email, name, street, city, state, zip_code) # <--- NEW SAVE STEP
             
             return response, None
        return None, "Signup failed (No user returned)"
    except Exception as e:
        return None, str(e)

# --- SIGN IN (UNCHANGED) ---
def sign_in(email, password):
    client, err = get_supabase_client()
    if err: return None, err
    
    try:
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            import database
            try:
                 database.create_or_get_user(email)
            except:
                 pass
            return response, None
        return None, str(e)
    except Exception as e:
        return None, str(e)

def get_current_address(email):
    import database
    try:
        user = database.get_user_by_email(email)
        if user:
            return {
                "name": user.address_name or "",
                "street": user.address_street or "",
                "city": user.address_city or "",
                "state": user.address_state or "",
                "zip": user.address_zip or ""
            }
    except Exception as e:
        print(f"Address Load Error: {e}")
    return {}