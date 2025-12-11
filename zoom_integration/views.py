import base64
import requests
from datetime import datetime
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from supabase import create_client

# Initialize Supabase client
supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

def get_zoom_access_token():
    """Get Zoom access token using account credentials."""
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={settings.ZOOM_ACCOUNT_ID}"
    auth_str = f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Zoom Token Error: {response.status_code} - {response.text}")
    return response.json()["access_token"]

def create_zoom_meeting(topic, start_time, duration):
    """Create a scheduled Zoom meeting."""
    token = get_zoom_access_token()
    
    # Format start_time to ISO 8601
    if hasattr(start_time, 'isoformat'):
        formatted_start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")  # UTC format
    else:
        formatted_start_time = start_time
    
    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": formatted_start_time,
        "duration": duration,
        "timezone": "Africa/Accra"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Zoom Meeting Creation Failed: {response.status_code} - {response.text}")
    
    return response.json()

# ------------------------------------------------------------------
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def schedule_meeting(request):
    topic = request.data.get("topic")
    start_time_str = request.data.get("start_time")
    duration = int(request.data.get("duration", 30))

    try:
        start_time = datetime.fromisoformat(start_time_str)
    except Exception as e:
        return Response({"error": f"Invalid start_time format: {e}"}, status=400)

    # Step 1: Create Zoom meeting
    try:
        meeting_info = create_zoom_meeting(topic, start_time, duration)
    except Exception as zoom_error:
        print("Zoom API Error:", zoom_error)
        return Response({"error": f"Zoom API Error: {zoom_error}"}, status=500)

    # Step 2: Insert meeting info into Supabase
    try:
        supabase.table("zoom_meetings").insert({
            "meeting_id": meeting_info.get("id"),    # Zoom meeting numeric ID
            "host_id": meeting_info.get("host_id"),  # <-- REQUIRED
            "topic": meeting_info.get("topic"),
            "start_time": meeting_info.get("start_time"),
            "duration": meeting_info.get("duration"),
            "join_url": meeting_info.get("join_url"),
            "start_url": meeting_info.get("start_url")
        }).execute()
    except Exception as supa_error:
        print("Supabase Insert Error:", supa_error)
        return Response({"error": f"Supabase Insert Error: {supa_error}"}, status=500)


    # Step 3: Return meeting info to frontend
    return Response({
        "topic": meeting_info.get("topic"),
        "start_time": meeting_info.get("start_time"),
        "duration": meeting_info.get("duration"),
        "join_url": meeting_info.get("join_url"),
        "start_url": meeting_info.get("start_url")
    })
