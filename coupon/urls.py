from django.urls import path
from . import views

urlpatterns = [
    path("", views.coupon_list, name="coupon_list"),
    path("add/", views.add_coupon, name="add_coupon"),
    path("apply/", views.apply_coupon, name="apply_coupon"),
    path("edit/<int:coupon_id>/",views.edit_coupon,name="edit_coupon",),
    path("toggle-status/<int:coupon_id>/",views.toggle_coupon_status,name="toggle_coupon_status",),
]
