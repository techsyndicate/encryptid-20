from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Player

def index(request):
    return render(request, 'pages/index.html')

def login(request):
    if request.method == "POST":
        username = request.POST['username'] 
        password = request.POST['password'] 

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'pages/login.html')

def register(request):
    if request.method == "POST":
        # get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is taken')
            return redirect('register')
        else:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is being used')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password, email=email,
                first_name=first_name, last_name=last_name)
                player = Player(user=user, banned=False, score=0, current_level=0)
                player.save()
                user.save()
                messages.success(request, 'You are now registered and can log in')
                return redirect('login')

    else:
        return render(request, 'pages/register.html')

@login_required(login_url='login')
def dashboard(request):
    current_user = User.objects.get(id=request.user.id)
    
    if current_user.player.banned == True:
        return render(request, 'pages/why-am-i-banned.html')
    else:
        return render(request, 'pages/dashboard.html')
    
@login_required(login_url='login')
def logout(request):
    if request.method == "POST":
        auth.logout(request)
        messages.success(request, 'You are now logged out')
    
    return redirect('index')