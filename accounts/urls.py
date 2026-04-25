from django.urls import path
from . import views





urlpatterns = [
    # path('', views.home_page, name='home_page'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),

    path('activate/<uidb64>/<token>/',views.activate,name='activate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword_validate'), 

    path('dashboard/', views.user_dashboard, name='dashboard'),   
    path('settings/', views.account_settings, name='account_settings'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('edit_email/', views.edit_email, name='edit_email'), 

    path('update_email_validate/<uidb64>/<token>/<str:encoded_email>/', views.update_email_validate, name='update_email_validate'),
]




