import requests
import streamlit as st

# Load Key
try:
    API_KEY = st.secrets["google"]["civic_key"]
except:
    API_KEY = None

def get_reps(address):
    """
    Returns a list of dictionaries: [{'name': '...', 'address': '...', 'title': '...'}]
    for the 2 US Senators and 1 US Representative.
    """
    if not API_KEY:
        return []

    url = "https://www.googleapis.com/civicinfo/v2/representatives"
    params = {
        'key': API_KEY,
        'address': address,
        'levels': 'country',
        'roles': ['legislatorUpperBody', 'legislatorLowerBody']
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()
        
        if "error" in data:
            print(f"Google API Error: {data['error']}")
            return []

        targets = []
        
        # Google separates "offices" (jobs) and "officials" (people). We match them up.
        for office in data.get('offices', []):
            # We only want Congress
            if "United States Senate" in office['name'] or "House of Representatives" in office['name']:
                for index in office['officialIndices']:
                    official = data['officials'][index]
                    
                    # Parse Address (Google returns a list, we take the first one)
                    addr_raw = official.get('address', [{}])[0]
                    clean_address = {
                        'name': official['name'],
                        'street': addr_raw.get('line1', ''),
                        'city': addr_raw.get('city', ''),
                        'state': addr_raw.get('state', ''),
                        'zip': addr_raw.get('zip', '')
                    }
                    
                    # Only add if we found a valid address
                    if clean_address['street']:
                        targets.append({
                            'name': official['name'],
                            'title': office['name'],
                            'address_obj': clean_address
                        })
        
        return targets

    except Exception as e:
        print(f"Civic Engine Error: {e}")
        return []
