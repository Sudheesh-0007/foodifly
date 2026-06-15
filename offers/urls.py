from django.urls import path
from . import views

urlpatterns = [
    path("", views.offer_list, name="offer_management"),
    path("add/", views.add_offer, name="add_offer"),
    path("edit/<int:offer_id>/", views.edit_offer, name="edit_offer"),
    path(
        "offers/toggle/<int:offer_id>/",
        views.toggle_offer_status,
        name="toggle_offer_status",
    ),
]
