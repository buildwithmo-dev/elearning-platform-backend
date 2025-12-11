from django.urls import path
from .views import create_user, login_user

urlpatterns = [
    path('signup/', create_user, name='signup'),
    path('login/', login_user, name='login'),
]