from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from supabase import create_client
from django.conf import settings
from .utils import get_user_from_token

# Initialize Supabase client
supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

def get_token(request):
    return request.headers.get("Authorization", "").replace("Bearer ", "")

# ================== Resources ==================
@api_view(['GET'])
@permission_classes([AllowAny])
def resources(request):
    try:
        result = supabase.table("resources").select("*").execute()
        return Response(result.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# ================== Course Categories ==================
@api_view(['GET'])
@permission_classes([AllowAny])
def course_categories(request):
    try:
        res = supabase.table("course_categories").select("*").execute()
        return Response(res.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def category_sections(request):
    try:
        res = supabase.table("course_categories") \
            .select("id, title, course(count)") \
            .execute()

        formatted_data = []
        for item in res.data:
            count_info = item.get('course', [])
            course_count = count_info[0].get('count', 0) if count_info else 0
            
            formatted_data.append({
                "id": item.get('id'),
                "title": item.get('title'),
                "course_count": course_count
            })

        return Response(formatted_data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# ================== Courses ==================
from urllib.parse import unquote

@api_view(["GET"])
@permission_classes([AllowAny])
def list_courses(request):
    try:
        category_param = request.query_params.get('category')
        
        # Start query joining the category table
        query = supabase.table("course").select("*, course_categories!inner(title)").eq("is_published", True)
        
        if category_param:
            # unquote handles special characters like %20 (space) or %2F (/)
            clean_category = unquote(category_param)
            query = query.eq("course_categories.title", clean_category)
            
        courses = query.execute()
        return Response(courses.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([AllowAny])
def course_detail(request, course_id):
    try:
        # 1. Fetch Course
        course_res = supabase.table("course").select("*").eq("id", course_id).single().execute()
        if not course_res.data:
            print(f"DEBUG: Course {course_id} not found.")
            return Response({"error": "Course not found"}, status=404)

        # 2. Fetch Modules (using 'module' singular)
        modules_res = supabase.table("module").select("id").eq("course_id", course_id).execute()
        module_ids = [m['id'] for m in modules_res.data]
        
        print(f"DEBUG: Found {len(module_ids)} modules for course {course_id}")

        if not module_ids:
            return Response([]) # This is likely what is returning []

        # 3. Fetch Lessons
        lessons_res = supabase.table("lesson") \
            .select("*") \
            .in_("module_id", module_ids) \
            .order("order") \
            .execute()
        
        print(f"DEBUG: Found {len(lessons_res.data)} lessons.")
        
        return Response(lessons_res.data)

    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return Response({"error": str(e)}, status=400)
    
@api_view(["POST"])
def create_course(request):
    try:
        token = get_token(request)
        user = get_user_from_token(token)

        # Verify instructor
        profile = supabase.table("profiles").select("is_instructor").eq("id", user.id).single().execute()
        if not profile.data or not profile.data.get("is_instructor"):
            return Response({"error": "Forbidden"}, status=403)

        # Prepare course data
        related_categories = request.data.get("related_categories")
        course_data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
            "price": request.data.get("price"),
            "is_published": request.data.get("is_published", False),
            "related_categories": related_categories[0] if related_categories else None,
            "instructor_id": user.id
        }

        # Insert course
        course_res = supabase.table("courses").insert(course_data).execute()
        if not course_res.data:
            return Response({"error": "Failed to create course"}, status=400)
        course_id = course_res.data[0]["id"]

        # Insert modules & lessons
        modules = request.data.get("modules", [])
        for mi, m in enumerate(modules, start=1):
            module_res = supabase.table("modules").insert({
                "title": m.get("title"),
                "course_id": course_id,
                "order": mi
            }).execute()
            if not module_res.data:
                continue
            module_id = module_res.data[0]["id"]

            for li, l in enumerate(m.get("lessons", []), start=1):
                content_url = l.get("content_url")

                # Handle file upload
                file_field = f"modules[{mi-1}][lessons][{li-1}][file]"
                file_obj = request.FILES.get(file_field)
                if file_obj:
                    filename = f"{user.id}_{file_obj.name}"
                    supabase.storage.from_("course-lessons").upload(filename, file_obj)
                    content_url = supabase.storage.from_("course-lessons").get_public_url(filename).public_url

                lesson_data = {
                    "title": l.get("title"),
                    "module_id": module_id,
                    "content_type": l.get("content_type", "video"),
                    "content_url": content_url,
                    "order": li
                }

                # Sandbox fields
                if l.get("content_type") == "sandbox":
                    lesson_data["language"] = l.get("language")
                    lesson_data["starter_code"] = l.get("starter_code")

                supabase.table("lessons").insert(lesson_data).execute()

        return Response({"status": "success", "course_id": course_id}, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(["GET"])
def course_students(request, course_id):
    try:
        token = get_token(request)
        user = get_user_from_token(token)
        course = supabase.table("courses").select("owner_id").eq("id", course_id).single().execute()
        if course.data["owner_id"] != user.id:
            return Response({"error": "Forbidden"}, status=403)
        students = supabase.table("enrollments").select("student_id, profiles(full_name,email)").eq("course_id", course_id).execute()
        return Response(students.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
