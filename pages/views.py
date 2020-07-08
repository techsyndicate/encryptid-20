from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import auth
import pyrebase
from .models import Player
from .db import db

firebaseConfig = {
    "apiKey": "AIzaSyAKNufpD5SwFkSdrWprl-OZTdJz9357z5U",
    "authDomain": "encryptid-20.firebaseapp.com",
    "databaseURL": "https://encryptid-20.firebaseio.com",
    "projectId": "encryptid-20",
    "storageBucket": "encryptid-20.appspot.com",
    "messagingSenderId": "877211524208",
    "appId": "1:877211524208:web:d3cca38f6c494d553be8b5"
}

firebase = pyrebase.initialize_app(firebaseConfig)

def index(request):
    return render(request, 'pages/index.html')

def login(request):
    if request.method == "POST":
        username = request.POST['username'] 
        password = request.POST['password']
        email = auth.get_user(username).email

        try:
            user = firebase.auth().sign_in_with_email_and_password(email, password)
            return redirect('dashboard')
        except Exception as e:
            messages.error(e)
            return redirect('login')

    else:
        return render(request, 'pages/login.html')

def register(request):
    if request.method == "POST":
        # get form values
        name = request.POST['name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = auth.create_user(
                uid=username,
                email=email,
                password=password,
                display_name=name
            )

            db.collection(u'users').document(user.uid).set({
                u'name': name,
                u'email': email,
                u'uid': user.uid,
                u'current_level': 0,
                u'points': 0,
                u'last_answer_time': 0,
                u'superuser': False
            })

            return redirect('login')

        except Exception as e:
            messages.error(request, e)
            return redirect('register')

    else:
        return render(request, 'pages/register.html')

def dashboard(request):
        return render(request, 'pages/dashboard.html')