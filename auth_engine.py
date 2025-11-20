import streamlit as st
# Import database for syncing
import database

# We do NOT initialize the client here anymore.
# We verify libraries exist, but don't connect yet.
try:
    from supabase import create_client, Client
    LIB_AVAILABLE = True
except ImportError:
    LIB_AVAILABLE = False

def get_client():
    """
    Connects to Supabase only when needed.
    """
    if not LIB_AVAILABLE:
        return None, "Library 'supabase' not installed."
        
    try:
        # Use .get() to avoid key errors
        url = st.secrets.get("supabase", {}).get("url", "")
        key = st.secrets.get("supabase", {}).get("key", "")
        
        if not url or not key:
            return None, "Missing Secrets: Check [supabase] section."
            
        return create_client(url, key), None
    except Exception as e:
        return None, str(e)

def sign_up(email, password):
    client, err = get_client()
    if err: return None, err
    
    try:
        response = client.auth.sign_up({"email": email, "password": password})
        if response.user:
             try:
                 database.create_or_get_user(email)
             except:
                 pass
             return response, None
        return None, "Signup failed (No user returned)"
    except Exception as e:
        return None, str(e)

def sign_in(email, password):
    client, err = get_client()
    if err: return None, err
    
    try:
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            try:
                 database.create_or_get_user(email)
            except:
                 pass
            return response, None
        return None, "Login failed"
    except Exception as e:
        return None, str(e)

def get_current_address(email):
    import database # Late import
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