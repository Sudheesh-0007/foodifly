
from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "main"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home ,name="home"),
    path('accounts/',include('accounts.urls')),
    path('admin-panel/',include('admin_panel.urls')),
    path('accounts/', include('allauth.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
