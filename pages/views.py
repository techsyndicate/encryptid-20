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

def index(request):
    return render(request, 'pages/index.html')

@login_required(login_url='login')
def dashboard(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user = db.collection(u'users').document(username).get().to_dict()
    completed_levels = len(user['completed_levels'])
    countries_color = user['countries_color']
    user_points = user['user_points']

    if user['banned']:
        return redirect('banned')
    
    c1color = countries_color['US']
    c2color = countries_color['CA']
    c3color = countries_color['RU']
    c4color = countries_color['AU']
    c5color = countries_color['TN']
    c6color = countries_color['GB']
    c7color = countries_color['CH']
    c8color = countries_color['SA']
    c9color = countries_color['BR']
    c10color = countries_color['CU']
    c11color = countries_color['FI']
    c12color = countries_color['GL']
    c13color = countries_color['LY']
    c14color = countries_color['NZ']
    c15color = countries_color['KW']
    c16color = countries_color['BG']

    context = {
        'c1color': c1color,
        'c2color': c2color,
        'c3color': c3color,
        'c4color': c4color,
        'c5color': c5color,
        'c6color': c6color,
        'c7color': c7color,
        'c8color': c8color,
        'c9color': c9color,
        'c10color': c10color,
        'c11color': c11color,
        'c12color': c12color,
        'c13color': c13color,
        'c14color': c14color,
        'c15color': c15color,
        'c16color': c16color,
        'username': username,
        'completed_levels': completed_levels,
        'points': user_points
    }

    return render(request, 'pages/dashboard.html', context)

@login_required(login_url='login')
def play(request, code):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()
    valid_levels = db.collection(u'levels').document('valid_levels').get().to_dict()['valid_levels']

    if code not in valid_levels:
        messages.error(request, "This is not a valid level.")
        return redirect('dashboard')
    else:
        if user['banned']:
            return redirect('banned')
        else:
            if code in user['completed_levels']:
                messages.success(request, "<i class='fa fa-check-square'></i>\t\tYou've already completed this level.")
                return redirect('dashboard')

            elif code == user['current_level'] or len(user['current_level']) == 0:
                user_doc.update({ u'current_level': code })
                level = db.collection(u'levels').document(code).get().to_dict()
                question = level['question']
                points = level['points']
                src_hint = level['src_hint']
                answer = level['answer']

            else:
                code = user['current_level']
                messages.error(request, "You must complete your level first.")
                return redirect('play', code=code)
        
            context = {
                'id': code,
                'question': question,
                'points': points,
                'hint': src_hint,
            }

            return render(request, 'pages/level.html', context)

def leaderboard(request):
    leaderboard = User.objects.filter(player__banned=False).order_by('-player__user_points', 'player__last_answer_time')
    context = { 'leaderboard': leaderboard }

    return render(request, 'pages/leaderboard.html', context)

@login_required(login_url='login')
def banned(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user = db.collection(u'users').document(username).get().to_dict()

    if not user['banned']:
        return redirect('dashboard')

    return render(request, 'pages/why-am-i-banned.html')

@login_required(login_url='login')
def waiting_page(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if not user['duels']:
        return redirect('dashboard')

    return render(request, 'pages/waiting_page.html')