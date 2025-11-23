import streamlit.components.v1 as components

def inject_ga():
    # YOUR MEASUREMENT ID
    measurement_id = 'G-D3P178CESF' 
    
    # This script logs to the browser console to help you debug if it's running
    ga_code = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{measurement_id}', {{
            'cookie_flags': 'SameSite=None;Secure'
        }});
        console.log("GA4 Injected: {measurement_id}");
    </script>
    """
    # height=0 ensures it's invisible but present
    components.html(ga_code, height=0, width=0)