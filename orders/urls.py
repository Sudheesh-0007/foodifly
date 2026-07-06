from django.urls import path

from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    path("invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("details/<int:order_id>", views.order_details, name="order_details"),
    path("cancel/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path(
        "cancel-item/<int:item_id>/", views.cancel_order_item, name="cancel_order_item"
    ),
    path("request-return/<int:item_id>/", views.request_return, name="request_return"),
    path(
        "verify-payment/",
        views.verify_payment,
        name="verify_payment",
    ),
    path("payment-failed/", views.payment_failed, name="payment_failed"),
]
