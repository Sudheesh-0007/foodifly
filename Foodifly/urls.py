from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, "404.html", status=404)


handler404 = "Foodifly.urls.custom_404" 



urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("accounts/", include("accounts.urls")),
    path("store/", include("store.urls")),
    path("admin-panel/", include("admin_panel.urls")),
    path("accounts/", include("allauth.urls")),
    path("admin-panel/categorys/", include("category.urls")),
    path("store/", include("store.urls")),
    path("cart/", include("cart.urls")),
    path("wishlist/", include("wishlist.urls")),
    path("orders/", include("orders.urls")),
    path("admin-panel/orders/", include("orders.admin_urls")),
    path("admin-panel/products/", include("store.admin_urls")),
    path("wallet/", include("wallet.urls")),
    path("admin-panel/offers/", include("offers.urls")),
    path("coupon/", include("coupon.urls")),
    path("reviews/", include("reviews.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
