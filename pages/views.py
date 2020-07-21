import requests
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from pages.db import db

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
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        name = f"{first_name} {last_name}"

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
                        u'name': name,
                        u'current_level': 0,
                        u'last_answer_time':0,
                        u'user_points': 0,
                        u'superuser': False,
                        u'banned': False,
                        u'email': email,
                        u'completed_levels': [],
                        u'current_level': ''
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
    completed_levels = len(user['completed_levels'])

    if user['banned']:
        return redirect('banned')
    else:
        context = {
            'username': username,
            'completed_levels': completed_levels
        }
        return render(request, 'pages/dashboard.html', context)

def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    
    return redirect('index')

@login_required(login_url='login')
def play(request, code):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if user['banned']:
        return redirect('banned')
    else:
        if code != user['current_level']:
            code = user['current_level']
            return redirect('play', code=code)
        else:
            user_doc.update({u'current_level': code})
            level = db.collection(u'levels').document(code).get().to_dict()
            question = level['question']
            points = level['points']
            src_hint = level['src_hint']
            answer = level['answer']
        
        context = {
            'id': code,
            'question': question,
            'points': points,
            'hint': src_hint
        }

        return render(request, 'pages/level.html', context)

@login_required(login_url='login')
def banned(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user = db.collection(u'users').document(username).get().to_dict()

    if not user['banned']:
        return redirect('dashboard')

    return render(request, 'pages/why-am-i-banned.html')
