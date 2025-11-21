import requests
import streamlit as st

# Load Key
try:
    API_KEY = st.secrets["geocodio"]["api_key"]
except:
    API_KEY = None

def get_reps(address):
    if not API_KEY:
        st.error("❌ Configuration Error: Geocodio API Key is missing.")
        return []

    url = "https://api.geocod.io/v1.7/geocode"
    params = {
        'q': address,
        'fields': 'cd', # Congressional District
        'api_key': API_KEY
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()

        if "error" in data:
            st.error(f"❌ Geocodio Error: {data['error']}")
            return []

        if not data.get('results'):
            st.warning("⚠️ Address not found.")
            return []

        result = data['results'][0]
        targets = []
        
        # Parse Congressional Data safely
        districts = result.get('fields', {}).get('congressional_districts', [])
        
        for district in districts:
            legislators = district.get('current_legislators', [])
            
            for leg in legislators:
                role = leg.get('type', 'unknown')
                title = "U.S. Senator" if role == 'senator' else "U.S. Representative"
                
                # SAFE NAME PARSING (The Fix)
                first = leg.get('bio', {}).get('first_name') or leg.get('first_name', 'Unknown')
                last = leg.get('bio', {}).get('last_name') or leg.get('last_name', 'Official')
                full_name = f"{first} {last}"
                
                # Safe Address Parsing
                contact = leg.get('contact', {})
                addr_raw = contact.get('address')
                if not addr_raw:
                    addr_raw = 'United States Capitol, Washington DC 20510'

                clean_address = {
                    'name': full_name,
                    'street': addr_raw,
                    'city': "Washington",
                    'state': "DC",
                    'zip': "20510"
                }

                # Deduplicate
                is_duplicate = False
                for t in targets:
                    if t['name'] == clean_address['name']:
                        is_duplicate = True
                
                if not is_duplicate:
                    targets.append({
                        'name': full_name,
                        'title': title,
                        'address_obj': clean_address
                    })

        if len(targets) == 0:
            st.warning("⚠️ Location found, but no legislators listed.")
        
        return targets

    except Exception as e:
        st.error(f"❌ Civic Engine Error: {e}")
        return []