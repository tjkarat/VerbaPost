import requests
import streamlit as st
import urllib.parse

# Load Key
try:
    API_KEY = st.secrets["google"]["civic_key"]
except:
    API_KEY = None

def get_reps(address):
    # 1. Sanity Check the Input
    if not address or len(address.strip()) < 10:
        st.error(f"❌ Address Error: The address sent to Google was too short: '{address}'")
        return []

    if not API_KEY:
        st.error("❌ Configuration Error: Google Civic API Key is missing in Secrets.")
        return []

    # 2. The Standard Endpoint
    url = "https://www.googleapis.com/civicinfo/v2/representatives"
    
    params = {
        'key': API_KEY,
        'address': address,
        'includeOffices': 'true'
    }

    # DEBUG: Print what we are sending (masked key)
    st.info(f"🔍 Searching Google Civic for: **{address}**")

    try:
        r = requests.get(url, params=params)
        
        # 3. Handle HTTP Errors
        if r.status_code == 404:
            st.error(f"❌ Google Error 404: The API could not find representatives for this specific address.")
            st.caption("Try formatting it like: '1600 Amphitheatre Pkwy, Mountain View, CA 94043'")
            return []
            
        if r.status_code == 403:
            st.error("❌ Google Error 403: Permission Denied.")
            st.info("Ensure the 'Civic Information API' is enabled in your Google Cloud Console.")
            return []

        data = r.json()
        
        if "error" in data:
            msg = data['error'].get('message', 'Unknown Error')
            st.error(f"❌ API Error: {msg}")
            return []

        targets = []
        
        # 4. Parse Results
        if 'offices' not in data:
            st.warning("⚠️ No representatives found.")
            return []

        for office in data.get('offices', []):
            name_lower = office['name'].lower()
            # Filter for Federal Congress
            if "senate" in name_lower or "senator" in name_lower or "house of representatives" in name_lower:
                
                for index in office['officialIndices']:
                    official = data['officials'][index]
                    
                    # Address Parsing (Handle missing addresses)
                    addr_list = official.get('address', [])
                    if not addr_list:
                        clean_address = {
                            'name': official['name'],
                            'street': 'United States Capitol',
                            'city': 'Washington',
                            'state': 'DC',
                            'zip': '20510'
                        }
                    else:
                        addr_raw = addr_list[0]
                        clean_address = {
                            'name': official['name'],
                            'street': addr_raw.get('line1', ''),
                            'city': addr_raw.get('city', ''),
                            'state': addr_raw.get('state', ''),
                            'zip': addr_raw.get('zip', '')
                        }
                    
                    targets.append({
                        'name': official['name'],
                        'title': office['name'],
                        'address_obj': clean_address
                    })
        
        return targets

    except Exception as e:
        st.error(f"❌ System Crash: {e}")
        return []