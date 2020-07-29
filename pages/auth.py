import requests, time, re, random
from dotenv import load_dotenv
from firebase_admin import firestore
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from pages.db import db
from pages.models import Player
from django.http import HttpResponseRedirect
from ratelimit.decorators import ratelimit
from django.http import HttpResponse
from datetime import datetime

def login(request):
    if request.method == "POST":
        username = request.POST['username'] 
        password = request.POST['password'] 

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            current_user = db.collection(u'users').document(username).get().to_dict()
            if current_user['superuser'] == True:
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

@ratelimit(key='ip', rate='2/d', method=['GET', 'POST'], block=True)
def register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        school = request.POST['school']
        discord_username = request.POST['discord_username']
        nc = request.POST.get('nc_check', False)
        nc = True if nc == "on" else False
        name = f"{first_name} {last_name}"

        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is taken.')
            return redirect('register')

        elif User.objects.filter(email=email).exists():
            messages.error(request, 'That email is being used.')
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
                player = Player(users=user)
                player.save()

                countries_color = {
                    'US':'red',
                    'CA':'red',
                    'RU': 'red',
                    'GL': 'red',
                    'BR': 'red',
                    'SA': 'red',
                    'TN': 'red',
                    'BG': 'red',
                    'NZ': 'red',
                    'AU': 'red',
                    'LY': 'red',
                    'CU': 'red',
                    'CH': 'red',
                    'FI': 'red',
                    'GB': 'red',
                    'JO': 'red'
                    }

                db.collection(u'users').document(username).set({
                    u'uid': username,
                    u'name': name,
                    u'school': school,
                    u'discord_username': discord_username,
                    u'nc': nc,
                    u'current_level': 0,
                    u'last_answer_time':0,
                    u'user_points': 0,
                    u'superuser': False,
                    u'banned': False,
                    u'email': email,
                    u'countries_color': countries_color,
                    u'completed_levels': [],
                    u'len_comp_levels': 0,
                    u'current_level': '',
                })
                r_msg = f'{username} has been registered successfully.'
                messages.success(request, r_msg)
                return redirect('index')

            else:
                messages.error(request, "Invalid reCAPTCHA. Please try again.")
                return redirect('register')

    context = { 'site_key': settings.RECAPTCHA_SITE_KEY }
    return render(request, 'pages/register.html', context)

def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    
    return redirect('index')