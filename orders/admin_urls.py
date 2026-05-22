from django.urls import path
from . import admin_views

urlpatterns = [
    path("", admin_views.admin_orders, name="admin_orders"),
    path("update-order-status/<int:order_id>/",admin_views.update_order_status,name="update_order_status",),
    path("returns/", admin_views.admin_return_requests, name="admin_return_requests"),
    path("returns/update/<int:item_id>/",admin_views.update_return_status,name="update_return_status",),
    path("details/<int:order_id>/",admin_views.admin_order_details,name="admin_order_details"),
]
