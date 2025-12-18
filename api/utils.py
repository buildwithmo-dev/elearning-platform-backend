import base64
import requests
from django.conf import settings
from supabase import create_client
from django.conf import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

def get_zoom_access_token():
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={settings.ZOOM_ACCOUNT_ID}"

    auth_str = f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, headers=headers)

    # DEBUG: print Zoom's error message
    if response.status_code != 200:
        print("\n\n====== ZOOM TOKEN ERROR ======")
        print("Status:", response.status_code)
        print("Response:", response.text)
        print("URL:", url)
        print("Auth header:", headers["Authorization"][:20] + "...")
        print("==============================\n\n")

    response.raise_for_status()
    return response.json()["access_token"]



# In utils.py, modify the signature if start_time is a Python datetime object
def create_zoom_meeting(topic, start_time, duration):
    token = get_zoom_access_token()

    # --- NEW: Convert datetime object to Zoom's required ISO 8601 string ---
    # Example: 2025-12-10T11:00:00
    # Use 'isoformat()' and remove the microseconds if they exist
    # NOTE: If start_time is already a string, you can skip this, but you must verify its format.
    if hasattr(start_time, 'isoformat'):
        formatted_start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S")
# This ensures it always includes the seconds part, :00 if necessary.
    else:
        # Assuming it's already a correctly formatted string if not a datetime object
        formatted_start_time = start_time
    
    url = "https://api.zoom.us/v2/users/me/meetings"
    # url = f"https://api.zoom.us/v2/users/{instructor_email}/meetings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "topic": topic,
        "type": 2,
        "start_time": formatted_start_time, # <-- USE THE NEW FORMATTED TIME
        "duration": duration,
        "timezone": "Africa/Accra"
    }
    # ... rest of the code

# In utils.py, inside create_zoom_meeting, just before the last line

    response = requests.post(url, json=payload, headers=headers)

    # --- START DEBUG BLOCK ---
    if response.status_code != 201: # Zoom returns 201 for meeting created
        print("\n" + "="*50)
        print("MEETING CREATION FAILED. ZOOM RESPONSE:")
        print(f"Status Code: {response.status_code}")
        try:
            # This will show the actual JSON error from Zoom
            print("Zoom Error Details (JSON):", response.json())
        except Exception:
            print("Zoom Error Details (Raw Text):", response.text)
        print(f"Payload Sent: {payload}")
        print("="*50 + "\n")
    # --- END DEBUG BLOCK ---

    response.raise_for_status()
    return response.json()

def get_user_from_token(token: str):
    if not token:
        raise Exception("Missing token")

    res = supabase.auth.get_user(token)
    if res.user is None:
        raise Exception("Invalid or expired token")

    return res.user