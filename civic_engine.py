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
    if not address or len(address.strip()) < 5:
        st.error("❌ Address Error: Address is too short or empty.")
        return []

    if not API_KEY:
        st.error("❌ Configuration Error: Google Civic API Key is missing.")
        return []

    # 2. The Official Endpoint (v2)
    base_url = "https://www.googleapis.com/civicinfo/v2/representatives"
    
    # 3. Correct Parameter Structure
    # We use a list for 'roles' so 'requests' formats it as &roles=...&roles=...
    params = {
        'key': API_KEY,
        'address': address,
        'levels': 'country',
        'roles': ['legislatorUpperBody', 'legislatorLowerBody']
    }

    try:
        # DEBUG: Print the sanitized URL (without key) to logs
        safe_address = urllib.parse.quote(address)
        print(f"🔍 Calling Google Civic for: {safe_address}")

        r = requests.get(base_url, params=params)
        
        # 4. Detailed Error Handling
        if r.status_code != 200:
            try:
                error_data = r.json()
                error_msg = error_data['error']['message']
                code = error_data['error']['code']
            except:
                error_msg = r.text
                code = r.status_code
                
            st.error(f"❌ Google API Error ({code}): {error_msg}")
            
            if code == 403:
                st.info("👉 Tip: Check Google Cloud Console -> APIs & Services. Ensure 'Civic Information API' is ENABLED.")
            if code == 404:
                st.info("👉 Tip: 404 usually means the Address format was rejected.")
            return []

        # 5. Success Processing
        data = r.json()
        targets = []

        if 'offices' not in data:
            st.warning("⚠️ Google found the address, but listed no representatives.")
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