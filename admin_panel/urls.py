from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('users/', views.admin_user_management, name='admin_user_management'),
    path('users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.report_dashboard, name='admin_report'),
    path("reports/export-excel/",views.export_sales_excel,name="export_sales_excel",),
    path("reports/export-pdf/",views.export_sales_pdf,name="export_sales_pdf"),
    path("sales-report/",views.sales_report,name="sales_report",),

    
]