# user_management/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from .models import User
from django.utils.crypto import get_random_string
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.barcode import code39
from reportlab.lib.units import inch
import os
from .models import PurchaseHistory
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .forms import PurchaseForm
from django.db.models import Sum
from datetime import datetime
from django.urls import reverse

def home(request):
    return render(request, 'user_management/home.html') 

def register_user(request):
    if request.method == 'POST':
        unique_id = get_random_string(12)
        user = User(
            unique_id=unique_id,
            name=request.POST['name'],
            age=request.POST['age'],
            gender=request.POST['gender'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            image=request.FILES['image'],
        )
        user.save()

        # Generate Aadhaar-style PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{user.name}_ID.pdf"'

        pdf = canvas.Canvas(response, pagesize=A4)
        pdf.setTitle("User ID Card")

        # Add user image
        image_path = user.image.path
        pdf.drawImage(image_path, 40, 700, width=1*inch, height=1.2*inch)

        # Add user details
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(160, 750, "User ID Card")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(160, 730, f"Name: {user.name}")
        pdf.drawString(160, 710, f"Age: {user.age}")
        pdf.drawString(160, 690, f"Gender: {user.gender}")
        pdf.drawString(160, 670, f"Phone: {user.phone}")
        pdf.drawString(160, 650, f"Email: {user.email}")

        # Add Unique ID
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(160, 630, f"Unique ID: {user.unique_id}")
        
        # Barcode for unique ID
        barcode = code39.Extended39(user.unique_id, barHeight=20, barWidth=1.5)
        barcode.drawOn(pdf, 160, 600)

        pdf.save()  
        return response

    return render(request, 'user_management/register.html')


def vendor_check(request):
    if request.method == 'POST':
        unique_id = request.POST['unique_id']
        user = User.objects.filter(unique_id=unique_id).first()
        
        if user:
            # Check if the user has exceeded the daily purchase limit
            today = timezone.now().date()
            purchases_today = PurchaseHistory.objects.filter(user=user, purchase_date=today).aggregate(total_bottles=Sum('bottle_count'))
            total_bottles_purchased = purchases_today['total_bottles'] or 0

            if total_bottles_purchased >= 2:
                messages.warning(request, f"{user.name} has reached the daily limit of 2 bottles.")
                return render(request, 'user_management/vendor_check.html', {'user': user, 'error': "Purchase limit exceeded for today."})
            else:
                return redirect('purchase_entry', user_id=user.id)
        else:
            messages.error(request, "User not found.")
    return render(request, 'user_management/vendor_check.html')
def purchase_entry(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        bottle_count = int(request.POST.get('bottle_count', 0))
        today = timezone.now().date()

        # Calculate total bottles including the current purchase
        purchases_today = PurchaseHistory.objects.filter(user=user, purchase_date=today).aggregate(total_bottles=Sum('bottle_count'))
        total_bottles_purchased = purchases_today['total_bottles'] or 0

        if total_bottles_purchased + bottle_count > 2:
            messages.error(request, "Exceeds daily limit of 2 bottles.")
            return render(request, 'user_management/purchase_entry.html', {'user': user})
        
        # Log purchase in PurchaseHistory
        PurchaseHistory.objects.create(user=user, bottle_count=bottle_count)
        messages.success(request, f"Purchase successful: {bottle_count} bottle(s) purchased.")
        return redirect(reverse('purchase_success', args=[user_id]))  # Redirect to a success page

    return render(request, 'user_management/purchase_entry.html', {'user': user})

def history(request, user_id):
    user = User.objects.get(id=user_id)
    
    # Get the date 7 days ago from today
    seven_days_ago = timezone.now().date() - timedelta(days=7)
    
    # Filter purchase history for the user in the past 7 days
    histories = PurchaseHistory.objects.filter(user=user, purchase_date__gte=seven_days_ago).order_by('-purchase_date')
    
    return render(request, 'user_management/history.html', {'user': user, 'histories': histories})

# user_management/views.py
def purchase_success(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'user_management/purchase_success.html', {'user': user})
