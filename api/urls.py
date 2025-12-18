from django.urls import path
from .views import (
    list_courses,
    course_detail,
    create_course,
    course_students,
    course_categories,
    category_sections,
    resources,  # ✅ add this back
)

urlpatterns = [
    path("resources/slides/", resources),
    path("courses/", list_courses),
    path("courses/<int:course_id>/", course_detail),
    path("courses/<int:course_id>/students/", course_students),
    path("courses/create-course", create_course),
    path("courses/categories/", course_categories),
    path("courses/category-section", category_sections),
]
