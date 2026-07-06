from django.urls import path

from . import views

urlpatterns = [
    # aadmin_side_urls
    path("", views.product_management, name="admin_products"),
    path("add/", views.add_product, name="add_product"),
    path("edit/<int:product_id>/", views.edit_product, name="edit_product"),
    path("delete/<int:product_id>/", views.delete_product, name="delete_product"),
    path("restore/<int:product_id>/", views.restore_product, name="restore_product"),
]
