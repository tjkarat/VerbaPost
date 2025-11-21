import requests
import streamlit as st
import urllib.parse

# Load Key
try:
    API_KEY = st.secrets["google"]["civic_key"]
except:
    API_KEY = None

def get_reps(address):
    # 1. Sanity Check
    if not address or len(address.strip()) < 10:
        st.error(f"❌ Address Error: The address is too short: '{address}'")
        return []

    if not API_KEY:
        st.error("❌ Configuration Error: Google Civic API Key is missing.")
        return []

    # 2. The Official Endpoint
    base_url = "https://www.googleapis.com/civicinfo/v2/representatives"
    
    params = {
        'key': API_KEY,
        'address': address,
        'levels': 'country',
        'roles': ['legislatorUpperBody', 'legislatorLowerBody']
    }

    try:
        # Debug: Print sanitized address to logs
        print(f"🔍 Calling Google Civic for: {address}")

        r = requests.get(base_url, params=params)
        
        # 3. Handle HTTP Errors
        if r.status_code != 200:
            try:
                err_json = r.json()
                error_msg = err_json['error']['message']
                code = err_json['error']['code']
            except:
                error_msg = r.text
                code = r.status_code
            
            st.error(f"❌ Google API Error ({code}): {error_msg}")
            
            if code == 400:
                st.info("👉 Tip: The address format was rejected. Try entering it exactly as it appears on a utility bill.")
            if code == 403:
                st.info("👉 Tip: Go to Google Cloud Console and ENABLE 'Civic Information API'.")
            return []

        data = r.json()
        targets = []

        if 'offices' not in data:
            st.warning("⚠️ Google found the location, but no representatives are listed.")
            return []

        for office in data.get('offices', []):
            name_lower = office['name'].lower()
            # Filter for Federal Congress
            if "senate" in name_lower or "senator" in name_lower or "representative" in name_lower:
                for index in office['officialIndices']:
                    official = data['officials'][index]
                    
                    # Parse Address (Handle missing/hidden addresses)
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
