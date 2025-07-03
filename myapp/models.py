from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    total_beds = models.IntegerField()
    per_bed_fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room_number}"

    def available_beds(self):
        occupied_beds = self.customers.count()
        return self.total_beds - occupied_beds

    def clean(self):
        if not (1 <= self.total_beds <= 10):
            raise ValidationError("Total beds must be between 5 and 10.")

class Customer(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='customers')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    joining_date = models.DateField()
    fee_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Room {self.room.room_number}"

    def clean(self):
        if self.room.available_beds() <= 0 and not self.pk:
            raise ValidationError(f"No available beds in Room {self.room.room_number}")
        if self.monthly_fee <= 0:
            raise ValidationError("Monthly fee must be greater than 0.")

    def update_fee_balance(self):
        """Calculate fee_balance based on months since joining and payments made."""
        today = datetime.now().date()
        start_date = self.joining_date
        months = []
        current_date = start_date
        while current_date <= today:
            months.append(current_date.strftime('%Y-%m'))
            current_date += relativedelta(months=1)
        
        total_due = len(months) * float(self.monthly_fee)
        total_paid = sum(float(payment.amount_paid) for payment in self.payments.filter(status='PAID'))
        self.fee_balance = max(0, total_due - total_paid)
        self.save()

class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    month = models.CharField(max_length=7)  # Format: YYYY-MM
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('OVERDUE', 'Overdue'),
    ], default='PENDING')

    def __str__(self):
        return f"{self.customer.name} - {self.month}"

class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ('FOOD', 'Food'),
        ('FURNITURE', 'Furniture'),
        ('INFRASTRUCTURE', 'Infrastructure'),
        ('MANAGEMENT_RENT', 'Management Rent'),
        ('EMPLOYEE_SALARY', 'Employee Salary'),
        ('Electricity','Electricity'),
        ('others','others'),
    ]
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.date}"