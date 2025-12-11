from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from supabase import create_client
from django.conf import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

@api_view(['GET'])
@permission_classes([AllowAny])
def resources(request):
    try:
        result = supabase.table("resources").select("*").execute()
        print(result.data[0]['url'])
        return Response(result.data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
