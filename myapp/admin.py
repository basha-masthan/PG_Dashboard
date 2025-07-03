from django.contrib import admin
from .models import Room, Customer, Payment, Expense

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'total_beds', 'per_bed_fee', 'available_beds')
    search_fields = ('room_number',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('room', 'name', 'phone_number', 'joining_date', 'fee_balance', 'monthly_fee')
    search_fields = ('room__room_number', 'name')
    list_filter = ('room', 'joining_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'month', 'amount_paid', 'payment_date', 'status')
    list_filter = ('status', 'month')
    search_fields = ('customer__name', 'month')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'date', 'description')
    list_filter = ('category', 'date')
    search_fields = ('category', 'description')