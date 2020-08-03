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

@login_required(login_url='login')
def admin_dashboard(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if not user['superuser']:
        return redirect('dashboard')

    return render(request, 'pages/admin_dashboard.html')

@login_required(login_url='login')
def users(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if not user['superuser']:
        return redirect('dashboard')

    users = User.objects.all()
    context = { 'users': users }

    return render(request, 'pages/users.html', context)

@login_required(login_url='login')
def user(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if not user['superuser']:
        return redirect('dashboard')

    if request.method == "POST":
        user_id = request.POST['user_id']
        user = db.collection(u'users').document(user_id).get().to_dict()

        if not user['superuser']:
            pass

        logs = db.collection(u'logs')
        logs = logs.where(u'username', u'==', user_id).order_by(u'timestamp', direction=firestore.Query.DESCENDING).limit(100)
        logs = logs.stream()
        log_docs = list(log.to_dict() for log in logs)
        y = "timestamp"
        for x in log_docs:
            new_timestamp = datetime.fromtimestamp(int(x.get(y)))
            x.update({y: new_timestamp})

        user = db.collection(u'users').document(user_id).get().to_dict()
        context = {
            'user': user,
            'log_docs':log_docs
        }

    return render(request, 'pages/user.html', context)

@login_required(login_url='login')
def delete_user(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if request.method == "POST":
        if not user['superuser']:
            pass

        user_id = request.POST['user_id']
        db.collection(u'users').document(user_id).delete()
        return redirect('users')

@login_required(login_url='login')
def ban_user(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if request.method == "POST":
        if not user['superuser']:
            pass

        user_id = request.POST['user_id']
        current_user = User.objects.get(username=user_id)
        user = db.collection(u'users').document(user_id)
        user.update({ u'banned': True })
        current_user.player.banned = True
        current_user.player.save(update_fields=["banned"])
        user = db.collection(u'users').document(user_id).get().to_dict()
        context = { 'user': user }
        return render(request, 'pages/user.html', context)

@login_required(login_url='login')
def unban_user(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if request.method == "POST":
        if not user['superuser']:
            pass

        user_id = request.POST['user_id']
        current_user = User.objects.get(username=user_id)
        user = db.collection(u'users').document(user_id)
        user.update({ u'banned': False })
        current_user.player.banned = False
        current_user.player.save(update_fields=["banned"])
        user = db.collection(u'users').document(user_id).get().to_dict()
        context = { 'user': user }
        return render(request, 'pages/user.html', context)

@login_required(login_url='login')
def levels(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if not user['superuser']:
        return redirect('dashboard')

    levels = db.collection(u'levels').stream()
    duel_levels = db.collection(u'duel_levels').stream()
    database = db
    context = { 'levels': levels, 'duel_levels' : duel_levels }

    return render(request, 'pages/admin_levels.html', context)

@login_required(login_url='login')
def level(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if not user['superuser']:
        return redirect('dashboard')

    if request.method == "POST":
        if not user['superuser']:
            pass

        level_id = request.POST['level_id'] 
        level = db.collection(u'levels').document(level_id).get().to_dict()
        context = {
            'level': level,
            'level_id':level_id,
        }

    return render(request, 'pages/admin_level.html', context)

@login_required(login_url='login')
def delete_level(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if request.method == "POST":
        if not user['superuser']:
            pass

        level_id = request.POST['level_id']
        db.collection(u'levels').document(level_id).delete()
        return redirect('levels')

@login_required(login_url='login')
def add_level(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if request.method == "POST":
        if not user['superuser']:
            pass

        level_id = request.POST['level_id']
        question = request.POST['question']
        src_hint = request.POST['src_hint']
        points = request.POST['points']
        answer = request.POST['answer']

        db.collection(u'levels').document(level_id).set({
            u'question': question,
            u'src_hint': src_hint,
            u'points': int(points),
            u'answer': answer,
            u'completed_by': 0
        })

        messages.error(request, "Level has been added.")
        return redirect('levels')

    return render(request, 'pages/add_level.html')

@login_required(login_url='login')
def assign_duels(request):
    users = db.collection(u'users').where(u'duels', u'==', True).stream()
    users = list(user.id for user in users)

    duel_levels = db.collection(u'duel_levels').where(u'completed', u'==', False).stream()
    duel_levels_list = list(level.id for level in duel_levels)

    # duplicate list elements to randomize duel level for all the players
    for i in range(len(duel_levels_list)):
        duel_levels_list.append(duel_levels_list[i])

    for user in users:
        user = db.collection(u'users').document(user)
        level_for_user = random.choice(duel_levels_list)
        duel_levels_list.remove(level_for_user)
        user.update({ u'current_duel_level': level_for_user })

    # 30 minutes time slot for one duel
    duel_end_time = time.time() + 1800
    duel_level_update = db.collection(u'duel_levels').where(u'completed', u'==', False).where(u'winner', u'==', '').stream()
    for level in db.collection(u'duel_levels').where(u'completed', u'==', False).where(u'winner', u'==', '').stream():
        level = db.collection(u'duel_levels').document(level.id)
        level.update({ u'end_time': duel_end_time })

    return redirect('admin_dashboard')

@login_required(login_url='login')
def delete_duel_level(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if request.method == "POST":
        if not user['superuser']:
            pass

        level_id = request.POST['level_id']
        db.collection(u'duel_levels').document(level_id).delete()
        return redirect('levels')


@login_required(login_url='login')
def add_duel_level(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if not user['superuser']:
        return redirect('dashboard')

    if request.method == "POST":
        level_id = request.POST['level_id']
        question = request.POST['question']
        src_hint = request.POST['src_hint']
        answer = request.POST['answer']

        db.collection(u'duel_levels').document(level_id).set({
            u'question': question,
            u'src_hint': src_hint,
            u'winning_points': 150,
            u'losing_points': 100,
            u'answer': answer,
            u'end_time': 0,
            u'completed': False,
            u'winner': "",
        })

        messages.error(request, "Duel Level has been added.")
        return redirect('levels')

    return render(request, 'pages/add_duel_level.html')

@login_required(login_url='login')
def logs(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if not user['superuser']:
        return redirect('dashboard')

    logs = db.collection(u'logs')
    logs = logs.order_by(u'timestamp', direction=firestore.Query.DESCENDING).limit(100).stream()
    log_docs = list(log.to_dict() for log in logs)
    y = "timestamp"
    for x in log_docs:
        new_timestamp = datetime.fromtimestamp(int(x.get(y)))
        x.update({y: new_timestamp})

    context = { 'log_docs': log_docs }

    return render(request, 'pages/logs.html', context)

@login_required(login_url='login')
def duel_level(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if not user['superuser']:
        return redirect('dashboard')

    if request.method == "POST":
        level_id = request.POST['level_id'] 
        level = db.collection(u'duel_levels').document(level_id).get().to_dict()
        context = {
            'level': level,
            'level_id':level_id,
        }

    return render(request, 'pages/admin_duel_level.html', context)
