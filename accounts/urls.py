from django.urls import path

from . import views

urlpatterns = [
    # path('', views.home_page, name='home_page'),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("forgot-password/", views.forgotPassword, name="forgotPassword"),
    path("reset-password/", views.resetPassword, name="resetPassword"),
    path(
        "reset-password-validate/<uidb64>/<token>/",
        views.resetpassword_validate,
        name="resetpassword_validate",
    ),
    path("dashboard/", views.user_dashboard, name="dashboard"),
    path("settings/", views.account_settings, name="account_settings"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("edit-email/", views.edit_email, name="edit_email"),
    path(
        "update-email-validate/<uidb64>/<token>/<str:encoded_email>/",
        views.update_email_validate,
        name="update_email_validate",
    ),
    path("address/", views.manage_addresses, name="address"),
    path("add-address/", views.add_address, name="add_address"),
    path("edit-address/<int:id>/", views.edit_address, name="edit_address"),
    path("delete-address/<int:id>/", views.delete_address, name="delete_address"),
    path(
    "resend-verification/",
    views.resend_verification,
    name="resend_verification",
)
]
