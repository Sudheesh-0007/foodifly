from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_management, name='admin_products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/',views.edit_product,name='edit_product'),
    path('products/delete/<int:product_id>/',views.delete_product,name='delete_product'),
    path('products/restore/<int:product_id>/',views.restore_product,name='restore_product'),
    
]