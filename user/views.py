from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from supabase import create_client
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password


supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    email = request.data.get("email")
    full_name = request.data.get("full_name", "")
    is_instructor = request.data.get("is_instructor", False)
    password = request.data.get("password")
    
    if not email:
        return Response({"error": "Email is required"}, status=400)

    try:
        # Check if user already exists
        existing = supabase.table("users").select("*").eq("email", email).execute()
        if existing.data and len(existing.data) > 0:
            return Response({"message": "User already exists", "user": existing.data[0]})

        hashed_password = make_password(password)
        
        # Insert new user
        user = supabase.table("users").insert({
            "email": email,
            "full_name": full_name,
            "is_instructor": is_instructor,
            "password": hashed_password
        }).execute()

        return Response({"message": "User created", "user": user.data[0]})

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email:
        return Response({"error": "Email field is missing"}, status=400)
    if not password:
        return Response({"error": "Password field is missing"}, status=400)

    try:
        # Fetch user by email
        result = supabase.table("users").select("*").eq("email", email).execute()
        user_data = result.data
        if not user_data:
            return Response({"error": "User not found"}, status=404)

        user = user_data[0]
        saved_hash = user.get("password")

        # Check password
        if not check_password(password, saved_hash):
            return Response({"error": "Incorrect password"}, status=401)

        return Response({"message": "Login successful", "user": user})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
