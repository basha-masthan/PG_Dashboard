from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-room/', views.add_room, name='add_room'),
    path('update-room/<int:room_id>/', views.update_room, name='update_room'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('add-customer/', views.add_customer, name='add_customer'),
    path('update-customer/<int:customer_id>/', views.update_customer, name='update_customer'),
    path('update-payment/<int:customer_id>/', views.update_payment, name='update_payment'),
    path('delete-customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),
    path('monthly-report/', views.monthly_report, name='monthly_report'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('payments/', views.payments_list, name='payments_list'),
]