from django.urls import path
from .views import resources

urlpatterns = [
    path("slides/", resources),
    # path("resources/<int:resource_id>/", resource_detail),
]
