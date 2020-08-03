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
from django.templatetags.static import static

@login_required(login_url='login')
@ratelimit(key='ip', rate='30/m', method=['GET', 'POST'], block=True)
def submit(request, code):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    total_players = User.objects.all().count()

    if request.method == "POST":
        answer = request.POST['answer']
        answer = ''.join(answer.split()).lower()

        current_level = user['current_level']
        level_doc = db.collection(u'levels').document(current_level)
        level = level_doc.get().to_dict()
        level_completed_by = level['completed_by']
        completed_levels = user['completed_levels']
        new_countries_color = user['countries_color']

        if level_doc.id == 'US':
            if answer == 'hallelujah':
                return redirect('https://drive.google.com/file/d/1HyAvomr3V-LBjmRC_oxCYHe3thBFhQO9/view?usp=sharing')

        if answer == level['answer']:
            completed_levels.append(current_level)
            new_countries_color[current_level] = '#16e16e'
            
            level_doc.update({ u'completed_by': level_completed_by + 1 })

            user_doc.update({
                u'current_level': '',
                u'last_answer_time': time.time(),
                u'completed_levels': completed_levels,
                u'len_comp_levels': len(completed_levels),
                u'countries_color': new_countries_color,
            })

            current_user.player.last_answer_time = time.time()
            current_user.player.num_completed_levels = len(completed_levels)
            current_user.player.save(update_fields=["last_answer_time", "num_completed_levels"])

            logs = db.collection(u'logs')
            logs.add({
                u'username': username,
                u'level': current_level,
                u'content': answer,
                u'timestamp': time.time()
            })

            messages.success(request, "Correct answer, good work there.")
            return redirect('dashboard')

        else:
            logs = db.collection(u'logs')
            logs.add({
                u'username': username,
                u'level': current_level,
                u'content': answer,
                u'timestamp': time.time()
            })
            messages.error(request, "<i class='fa fa-times'></i>\t\tIncorrect answer.")
            return redirect('play', code=current_level)

@login_required(login_url='login')
@ratelimit(key='ip', rate='30/m', method=['GET', 'POST'], block=True)
def skip_level(request, code):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    total_players = User.objects.all().count()

    level_doc = db.collection(u'levels').document(code)
    level = level_doc.get().to_dict()
    level_points = level['points']
    level_completed_by = level['completed_by']
    completed_levels = user['completed_levels']
    completed_levels.append(code)

    new_countries_color = user['countries_color']
    new_countries_color[code] = '#16e16e'

    user_doc.update({
        u'completed_levels': completed_levels,
        u'len_com_levels': len(completed_levels),
        u'current_level': '',
        u'countries_color': new_countries_color
    })

    current_user.player.num_completed_levels = len(completed_levels)
    current_user.player.save(update_fields=['num_completed_levels'])

    logs = db.collection(u'logs')
    logs.add({
        u'username': username,
        u'level': code,
        u'content': 'Skipped level',
        u'timestamp': time.time()
    })

    return redirect('dashboard')

@login_required(login_url='login')
def play_duel(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()
    user_points = user['user_points']

    if user['banned']:
        return redirect('banned')

    if 'duels' not in user.keys():
        return redirect('dashboard')

    if not user['duels']:
        return redirect('dashboard')

    if not user['current_duel_level']:
        return redirect('waiting_page')

    # if duel_level['winner']:
    #     if username != duel_level['winner']:
    #         messages.success(request, f"Hard luck, {opponent} has completed the level.")

    current_duel_level = user['current_duel_level']
    duel_level_doc = db.collection(u'duel_levels').document(current_duel_level)
    duel_level = duel_level_doc.get().to_dict()
    current_players = duel_level['players']
    winning_points = duel_level['winning_points']
    losing_points = duel_level['losing_points']
    question = duel_level['question']
    src_hint = duel_level['src_hint']
    end_time = duel_level['end_time']
    opponent = [player for player in current_players if player != username][0]

    if time.time() > duel_level['end_time']:
        return redirect('waiting_page')

    if request.method == 'POST':
        answer = request.POST['answer']
        answer = ''.join(answer.split()).lower()

        if answer == duel_level['answer']:
            if not duel_level['winner']:
                duel_level_doc.update({ u'winner': username })
                user_doc.update({
                    u'user_points': user_points + winning_points,
                    u'last_answer_time': time.time(),
                    u'current_duel_level': ''
                })
                messages.success(request, f"Congratulations! You've won this duel round against {opponent}.")
                return redirect('waiting_page')

            else:
                duel_level_doc.update({ u'loser': username })
                user_doc.update({
                    u'user_points': user_points + losing_points,
                    u'last_answer_time': time.time(),
                    u'current_duel_level': ''
                })
                duel_level_doc.update({ u'completed': True })
                messages.success(request, f"Correct answer, but {opponent} won this duel round.")
                return redirect('waiting_page')

        else:
            logs = db.collection(u'logs')
            logs.add({
                u'username': username,
                u'level': current_duel_level,
                u'content': answer,
                u'timestamp': time.time()
            })
            messages.error(request, "<i class='fa fa-times'></i>\t\tIncorrect answer.")
            return redirect('play_duel')
    
    context = {
        'opponent': opponent,
        'question': question,
        'hint': src_hint,
        'end_time': end_time
    }

    return render(request, 'pages/duel_level.html', context)