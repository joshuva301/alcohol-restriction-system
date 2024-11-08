# user_management/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register_user, name='register_user'),
    path('vendor-check/', views.vendor_check, name='vendor_check'),
    path('purchase-entry/<int:user_id>/', views.purchase_entry, name='purchase_entry'),
    path('history/<int:user_id>/', views.history, name='history'),
    path('purchase-success/<int:user_id>/', views.purchase_success, name='purchase_success'),
]
