from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('manage/', views.manage_tickets, name='manage_tickets'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),  # Add this line
    path('tickets/<int:pk>/delete/', views.delete_ticket, name='delete_ticket'),  # Add this
    path('update/<int:ticket_id>/', views.update_ticket, name='update_ticket'),
]
