import requests
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from pages.db import db
from django.http import HttpResponseRedirect


def index(request):
    return render(request, 'pages/index.html')

def login(request):
    if request.method == "POST":
        username = request.POST['username'] 
        password = request.POST['password'] 

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            if user.username == "anshul":
                auth.login(request, user)
                messages.success(request, 'You are now logged in')
                return redirect('admin_dashboard')
            else:
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
                recaptcha_response = request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.RECAPTCHA_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()

                if result['success']:
                    user = User.objects.create_user(username=username, password=password, email=email,
                    first_name=first_name, last_name=last_name)
                    user.save()

                    db.collection(u'users').document(username).set({
                        u'uid': username,
                        u'name':first_name,
                        u'current_level': 0,
                        u'last_answer_time':0,
                        u'user_points': 0,
                        u'superuser': False,
                        u'banned': False,
                        u'email': email,
                    })

                    messages.success(request, 'You are now registered and can log in')
                    return redirect('login')
                else:
                    messages.error(request, "Invalid reCAPTCHA. Please try again.")
                    return redirect('register')

    else:
        context = { 'site_key': settings.RECAPTCHA_SITE_KEY }
        return render(request, 'pages/register.html', context)

@login_required(login_url='login')
def dashboard(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user = db.collection(u'users').document(username).get().to_dict()
    if user['banned']:
        return render(request, 'pages/why-am-i-banned.html')
    else:
        return render(request, 'pages/dashboard.html')
    

def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    
    return redirect('index')

def level_call(request, code):
    print(code)
    return redirect('dashboard')


@login_required(login_url='login')
def admin_dashboard(request):
    return render(request, 'pages/admin_dashboard.html')

@login_required(login_url='login')
def users(request):
    users = db.collection(u'users').stream()
    database = db
    context = {
        'users': users,
        'database': database
    }

    return render(request, 'pages/users.html', context)


@login_required(login_url='login')
def user(request):
    if request.method == "POST":
        user_id = request.POST['user_id'] 
        user = db.collection(u'users').document(user_id).get().to_dict()
        context = {
            'user': user,
        }
        return render(request, 'pages/user.html', context)

@login_required(login_url='login')
def delete_user(request):
    if request.method == "POST":
        user_id = request.POST['user_id']
        db.collection(u'users').document(user_id).delete()
        return redirect('users')

@login_required(login_url='login')
def ban_user(request):
    if request.method == "POST":
        user_id = request.POST['user_id']
        user = db.collection(u'users').document(user_id)
        user.update({u'banned': True})
        user = db.collection(u'users').document(user_id).get().to_dict()
        context = {
            'user': user,
        }
        return render(request, 'pages/user.html', context)

@login_required(login_url='login')
def unban_user(request):
    if request.method == "POST":
        user_id = request.POST['user_id']
        user = db.collection(u'users').document(user_id)
        user.update({u'banned': False})
        user = db.collection(u'users').document(user_id).get().to_dict()
        context = {
            'user': user,
        }
        return render(request, 'pages/user.html', context)




