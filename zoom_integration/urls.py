from django.urls import path
from .views import schedule_meeting

urlpatterns = [
    path('create-meeting/', schedule_meeting, name='create-meeting'),
]
