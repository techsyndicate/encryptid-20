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

def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    
    return redirect('index')