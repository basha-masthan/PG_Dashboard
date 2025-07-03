from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from .models import Room, Customer, Payment, Expense
from django.core.exceptions import ValidationError

def dashboard(request):
    balance_filter = request.GET.get('balance_filter', '')
    customers = Customer.objects.all().order_by('room__room_number')
    rooms = Room.objects.all()
    # Update fee_balance for all customers
    for customer in customers:
        customer.update_fee_balance()
    if balance_filter == 'unpaid':
        customers = customers.filter(fee_balance__gt=0).order_by('room__room_number')
    
    rooms_data = [
        {
            'room': room,
            'occupancy_percentage': (room.customers.count() / room.total_beds * 100) if room.total_beds > 0 else 0,
            'occupied_beds': room.customers.count(),
            'total_beds': room.total_beds
        }
        for room in rooms
    ]
    
    return render(request, 'dashboard.html', {
        'customers': customers,
        'rooms_data': rooms_data,
        'balance_filter': balance_filter
    })

def add_room(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        total_beds = request.POST.get('total_beds')
        per_bed_fee = request.POST.get('per_bed_fee')
        
        try:
            room = Room(room_number=room_number, total_beds=total_beds, per_bed_fee=per_bed_fee)
            room.full_clean()
            room.save()
            messages.success(request, 'Room added successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error adding room: {str(e)}')
    
    return render(request, 'room_form.html', {'form_title': 'Add Room'})

def update_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        total_beds = request.POST.get('total_beds')
        per_bed_fee = request.POST.get('per_bed_fee')
        
        try:
            room.room_number = room_number
            room.total_beds = total_beds
            room.per_bed_fee = per_bed_fee
            room.full_clean()
            room.save()
            messages.success(request, f'Room {room.room_number} updated successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error updating room: {str(e)}')
    
    return render(request, 'room_form.html', {'form_title': f'Update Room {room.room_number}', 'room': room})

def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        try:
            if room.customers.count() > 0:
                messages.error(request, f'Cannot delete Room {room.room_number} because it has {room.customers.count()} customers.')
            else:
                room.delete()
                messages.success(request, f'Room {room.room_number} deleted successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error deleting room: {str(e)}')
    return render(request, 'room_form.html', {
        'form_title': f'Confirm Delete Room {room.room_number}',
        'room': room,
        'is_delete': True
    })

def add_customer(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        joining_date = request.POST.get('joining_date')
        monthly_fee = request.POST.get('monthly_fee')
        
        try:
            room = Room.objects.get(id=room_id)
            customer = Customer(
                room=room,
                name=name,
                phone_number=phone_number,
                joining_date=joining_date,
                monthly_fee=monthly_fee,
                fee_balance=monthly_fee
            )
            customer.full_clean()
            customer.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error adding customer: {str(e)}')
    
    rooms = Room.objects.all()
    return render(request, 'customer_form.html', {'form_title': 'Add Customer', 'rooms': rooms})

def update_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        room_id = request.POST.get('room')
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        joining_date = request.POST.get('joining_date')
        monthly_fee = request.POST.get('monthly_fee')
        
        try:
            room = Room.objects.get(id=room_id)
            if room != customer.room and room.available_beds() <= 0:
                raise ValidationError(f"No available beds in Room {room.room_number}")
            customer.room = room
            customer.name = name
            customer.phone_number = phone_number
            customer.joining_date = joining_date
            customer.monthly_fee = monthly_fee
            customer.full_clean()
            customer.save()
            customer.update_fee_balance()  # Recalculate balance after monthly_fee change
            messages.success(request, f'Customer {customer.name} updated successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error updating customer: {str(e)}')
    
    rooms = Room.objects.all()
    return render(request, 'customer_form.html', {
        'form_title': f'Update Customer {customer.name}',
        'customer': customer,
        'rooms': rooms
    })

def update_payment(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    current_month = datetime.now().strftime('%Y-%m')
    
    if request.method == 'POST':
        amount_paid = request.POST.get('amount_paid')
        status = request.POST.get('status')
        month = request.POST.get('month')
        
        try:
            if not month or not len(month) == 7 or month[4] != '-':
                raise ValidationError("Month must be in YYYY-MM format")
            Payment.objects.create(
                customer=customer,
                month=month,
                amount_paid=amount_paid,
                status=status
            )
            customer.update_fee_balance()  # Recalculate balance after payment
            messages.success(request, f'Payment of {amount_paid} for {month} added for {customer.name}')
            return render(request, 'customer_form.html', {
                'form_title': f'Update Payment for {customer.name}',
                'customer': customer,
                'current_month': current_month
            })
        except Exception as e:
            messages.error(request, f'Error adding payment: {str(e)}')
            return render(request, 'customer_form.html', {
                'form_title': f'Update Payment for {customer.name}',
                'customer': customer,
                'current_month': current_month
            })
    
    return render(request, 'customer_form.html', {
        'form_title': f'Update Payment for {customer.name}',
        'customer': customer,
        'current_month': current_month
    })

def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        try:
            customer.delete()
            messages.success(request, f'Customer {customer.name} deleted successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error deleting customer: {str(e)}')
    return render(request, 'customer_form.html', {
        'form_title': f'Confirm Delete {customer.name}',
        'customer': customer,
        'is_delete': True
    })

def monthly_report(request):
    collections = Payment.objects.annotate(
        month_trunc=TruncMonth('payment_date')
    ).values('month_trunc').annotate(total_collected=Sum('amount_paid')).order_by('-month_trunc')
    
    expenses = Expense.objects.annotate(
        month_trunc=TruncMonth('date')
    ).values('month_trunc').annotate(total_expenses=Sum('amount')).order_by('-month_trunc')
    
    return render(request, 'monthly_report.html', {
        'collections': collections,
        'expenses': expenses
    })

def add_expense(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('date')
        
        try:
            Expense.objects.create(
                category=category,
                amount=amount,
                description=description,
                date=date
            )
            messages.success(request, 'Expense added successfully!')
            return redirect('monthly_report')
        except Exception as e:
            messages.error(request, f'Error adding expense: {str(e)}')
    
    return render(request, 'expense_form.html', {'form_title': 'Add Expense'})

def payments_list(request):
    payments = Payment.objects.select_related('customer', 'customer__room').order_by('-payment_date')
    # Update fee_balance for all customers
    for payment in payments:
        payment.customer.update_fee_balance()
    return render(request, 'payments_list.html', {'payments': payments})