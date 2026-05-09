from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_management, name='category_management'),
    path('add/', views.add_category, name='add_category'),
    path('categories/edit/<slug:category_slug>/', views.edit_category, name='edit_category'),
    path('categories/delete/<slug:category_slug>/', views.soft_delete_category, name='delete_category'),
    path('category/restore/<slug:slug>/',views.restore_category,name='restore_category'),


]