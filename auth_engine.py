import streamlit as st

# Try to import library, but don't crash if missing
try:
    from supabase import create_client, Client
    LIB_AVAILABLE = True
except ImportError:
    LIB_AVAILABLE = False

def get_supabase_client():
    """
    Connects to Supabase only when requested.
    Returns: (Client, ErrorString)
    """
    if not LIB_AVAILABLE:
        return None, "Library 'supabase' not installed."

    try:
        # Use .get() to avoid KeyErrors if secrets are missing
        # This prevents the "Blank Page" crash
        supabase_secrets = st.secrets.get("supabase", None)
        
        if not supabase_secrets:
            return None, "Missing [supabase] section in Secrets."
            
        url = supabase_secrets.get("url")
        key = supabase_secrets.get("key")
        
        if not url or not key:
            return None, "Missing 'url' or 'key' inside [supabase] secrets."
            
        return create_client(url, key), None
        
    except Exception as e:
        return None, f"Connection Error: {e}"

def sign_up(email, password):
    client, err = get_supabase_client()
    if err: return None, err
    
    try:
        response = client.auth.sign_up({"email": email, "password": password})
        # Lazy Import Database to avoid circular dependencies
        import database
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
        return None, "Login failed"
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