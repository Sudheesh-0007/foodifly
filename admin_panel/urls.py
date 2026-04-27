from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('users/', views.admin_user_management, name='admin_user_management'),
    path('users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
]