from django.urls import path
from .import views
from billing.models import Billing, Payment

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Home page for users
    path('bills/', views.view_bills, name='view_bills'),  # View all bills
    path('bills/<int:billing_id>/', views.view_bill_details, name='bill_details'),  # Bill details
    path('bills/<int:billing_id>/pay/', views.pay_bill, name='pay_bill'),  # Payment page
]


