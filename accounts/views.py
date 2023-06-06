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

def forgot_password(request):
    if request.method=="POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return render(request,"accounts/forgot_password.html")
        token = str(uuid.uuid4())
        user.pwd_reset_token = token
        user.save()
        domain_name = request.headers['Origin']
        relative_path = reverse("reset_password",args=[token])
        url = f"{domain_name}{relative_path}"
        message = send_password_reset_email(url,user.email)
        if message:
            messages.success(request,"A verification code has been sent to your phone.")
        else:
            messages.error(request, "Something went wrong")
        return redirect("reset_password",user.id)
    
    return render(request,"accounts/forgot_password.html")

# Reset password view
def reset_password(request,token):
    try:
        user = User.objects.get(pwd_reset_token=token)
    except User.DoesNotExist:
        return redirect("forgot_password")
    
    if request.method=="POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")

        if user.pwd_reset_token != token:
            messages.error(request, "Verification code is incorrect.")
            return redirect("reset_password",token)
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password",token)
        
        user.set_password(new_password)
        user.pwd_reset_token = ""
        user.save()
        messages.success(request,"Your password has been changed.")
        return redirect("login")
    
    return render(request,"accounts/reset_password.html")