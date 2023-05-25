from django.shortcuts import render,redirect
from .models import User
from .helper import send_password_reset_email
import uuid
from django.urls import reverse
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('confirm-password')

        user = User.objects.filter(email=email).exists()
        if user:
            messages.error(request,'User already exists')
            return render(request,'accounts/signup.html')
        
        if password != password2:
            messages.error(request,'Passwords do not match')
            return render(request,'accounts/signup.html')
        
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        messages.success(request,'Account has been created successfully')
        return render(request,'accounts/signup.html')        
    return render(request,'accounts/signup.html')

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request,'User does not exist')
            return render(request,'accounts/login.html')
        
        if not user.check_password(password):
            messages.error(request,'Incorrect password')
            return render(request,'accounts/login.html')
        
        user = authenticate(request, username=email, password=password)
        if user is None:
            return render(request,'accounts/login.html')
        login(request, user)
        return redirect('/')

    return render(request, 'accounts/login.html')

@login_required(login_url='/accounts/login/')
def logout_view(request):
    logout(request)
    return render(request,'accounts/login.html')

