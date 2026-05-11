from django.urls import path

from . import views

urlpatterns = [
    path("", views.cart, name="cart"),
    path("add/<int:product_id>/", views.add_cart, name="add_cart"),
    path(
        "increase/<int:cart_item_id>/",
        views.increase_cart_quantity,
        name="increase_cart_quantity",
    ),
    path(
        "decrease/<int:cart_item_id>/",
        views.decrease_cart_quantity,
        name="decrease_cart_quantity",
    ),
    path("remove/<int:cart_item_id>/", views.remove_cart_item, name="remove_cart_item"),
]
