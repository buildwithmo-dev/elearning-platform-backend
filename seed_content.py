import os
from supabase import create_client

# --- CONFIGURATION ---
URL = "https://hatlulnezssdimbqwhin.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhhdGx1bG5lenNzZGltYnF3aGluIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTM2MjYxMiwiZXhwIjoyMDgwOTM4NjEyfQ.Z-v19g13PnDNEzpczwRoKG6mdlrxON44Qny2AEovLqM"
supabase = create_client(URL, KEY)

def seed_all_courses():
    try:
        # 1. Fetch all courses
        courses = supabase.table("course").select("id, title").execute()
        course_list = courses.data

        print(f"Found {len(course_list)} courses. Starting clean seed...")

        module_templates = [
            "Module 1: Foundations & Setup",
            "Module 2: Core Concepts",
            "Module 3: Advanced Techniques",
            "Module 4: Project & Certification"
        ]

        lesson_templates = [
            {"title": "Welcome & Overview", "type": "video", "url": "https://example.com/v1"},
            {"title": "Technical Documentation", "type": "document", "url": "https://example.com/doc1.pdf"},
            {"title": "Hands-on Practice Lab", "type": "sandbox", "url": '{"code": "print(\'Hello World\')"}'},
            {"title": "Expert Interview", "type": "video", "url": "https://example.com/v2"},
            {"title": "Module Assessment", "type": "document", "url": "https://example.com/quiz.pdf"}
        ]

        for course in course_list:
            course_id = course['id']
            print(f"Processing Course {course_id}: {course['title']}...")

            # --- CLEANUP STEP ---
            module_data = supabase.table("module").select("id").eq("course_id", course_id).execute()
            if module_data.data:
                m_ids = [m['id'] for m in module_data.data]
                # Delete lessons first to avoid foreign key violations
                supabase.table("lesson").delete().in_("module_id", m_ids).execute()
                supabase.table("module").delete().eq("course_id", course_id).execute()

            for m_idx, m_title in enumerate(module_templates, 1):
                # 2. Insert Module
                m_res = supabase.table("module").insert({
                    "title": m_title,
                    "course_id": course_id,
                    "order": m_idx
                }).execute()

                if m_res.data:
                    module_id = m_res.data[0]['id']
                    
                    # 3. Prepare Lessons (REMOVED 'description' column)
                    lesson_batch = []
                    for l_idx, l_temp in enumerate(lesson_templates, 1):
                        lesson_batch.append({
                            "title": f"{l_temp['title']} ({m_title})",
                            "module_id": module_id,
                            "content_type": l_temp['type'],
                            "content_url": l_temp['url'],
                            "order": l_idx
                        })
                    
                    supabase.table("lesson").insert(lesson_batch).execute()

        print("\n✅ Success! All 480 courses re-seeded without description errors.")

    except Exception as e:
        print(f"\n❌ Script Failed: {str(e)}")

if __name__ == "__main__":
    seed_all_courses()