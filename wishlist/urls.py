from django.urls import path
from . import views

urlpatterns = [
    path("add-to-wishlist/", views.add_to_wishlist, name="add_to_wishlist"),
    path("remove/<int:item_id>/", views.remove_wishlist_item, name="remove_wishlist_item"),
    path('',views.wishlist_page,name='wishlist_page'),
]
