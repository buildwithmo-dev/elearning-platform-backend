from django.urls import path
from .views import resources, course_categories, category_sections

urlpatterns = [
    path("resources/slides/", resources),
    # path("resources/<int:resource_id>/", resource_detail),
    path("courses/categories/", course_categories),
    path("courses/category-section", category_sections)
]
