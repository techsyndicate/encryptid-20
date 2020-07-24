import requests, time
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

def index(request):
    return render(request, 'pages/index.html')

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

        elif User.objects.filter(email=email).exists():
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
                player = Player(users=user)
                player.save()

                countries_color = {'US':'red','CA':'red','IN':'red'}

                db.collection(u'users').document(username).set({
                    u'uid': username,
                    u'name': name,
                    u'current_level': 0,
                    u'last_answer_time':0,
                    u'user_points': 0,
                    u'superuser': False,
                    u'banned': False,
                    u'email': email,
                    u'countries_color':countries_color,
                    u'completed_levels': [],
                    u'len_comp_levels': 0,
                    u'current_level': '',
                })
                messages.success(request, 'You are now registered and can log in')
                return redirect('login')

            else:
                messages.error(request, "Invalid reCAPTCHA. Please try again.")
                return redirect('register')

    context = { 'site_key': settings.RECAPTCHA_SITE_KEY }
    return render(request, 'pages/register.html', context)

@login_required(login_url='login')
def dashboard(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user = db.collection(u'users').document(username).get().to_dict()
    completed_levels = len(user['completed_levels'])
    countries_color = user['countries_color']

    if user['banned']:
        return redirect('banned')
    
    c1color,c2color,c3color = countries_color['US'],countries_color['CA'],countries_color['IN']
    context = {
        'c1color':c1color,
        'c2color':c2color,
        'c3color':c3color,
        'username': username,
        'completed_levels': completed_levels,
        'lolthis': 'red'
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
    valid_levels = db.collection(u'levels').document('valid_levels').get().to_dict()['valid_levels']

    if code not in valid_levels:
        messages.error(request, "This is not a valid level.")
        return redirect('dashboard')
    else:
        if user['banned']:
            return redirect('banned')
        else:
            if code in user['completed_levels']:
                messages.success(request, "You've already completed this level.")
                return redirect('dashboard')

            elif code == user['current_level'] or len(user['current_level']) == 0:
                user_doc.update({u'current_level': code})
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

@login_required(login_url='login')
def banned(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user = db.collection(u'users').document(username).get().to_dict()

    if not user['banned']:
        return redirect('dashboard')

    return render(request, 'pages/why-am-i-banned.html')

@login_required(login_url='login')
def admin_dashboard(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if user['superuser']:
        return render(request, 'pages/admin_dashboard.html')

    return redirect('dashboard')

@login_required(login_url='login')
def users(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if user['superuser']:
        users = db.collection(u'users').stream()
        context = { 'users': users }
        return render(request, 'pages/users.html', context)

    return redirect('dashboard')

@login_required(login_url='login')
def user(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if user['superuser']:
        if request.method == "POST":
            user_id = request.POST['user_id'] 
            user = db.collection(u'users').document(user_id).get().to_dict()
            context = { 'user': user }
            return render(request, 'pages/user.html', context)

    return redirect('dashboard')

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
    if request.method == "POST":
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
def submit(request, code):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    num_completed_levels = current_user.player.num_completed_levels
    last_answer_time = current_user.player.last_answer_time
    player_points = current_user.player.user_points
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if request.method == "POST":
        answer = request.POST['answer']
        answer = ''.join(answer.split()).lower()

        current_level = user['current_level']
        level = db.collection(u'levels').document(current_level).get().to_dict()
        level_points = level['points']
        completed_levels = user['completed_levels']
        user_points = user['user_points']
        new_countries_color = user['countries_color']

        if answer == level['answer']:
            completed_levels.append(current_level)
            new_countries_color[current_level] = 'green'

            user_doc.update({
                u'current_level': '',
                u'last_answer_time': time.time(),
                u'completed_levels': completed_levels,
                u'len_comp_levels': len(completed_levels),
                u'user_points': user_points + level_points,
                u'countries_color':new_countries_color,
            })

            current_user.player.last_answer_time = time.time()
            current_user.player.num_completed_levels = len(completed_levels)
            current_user.player.user_points += level_points
            current_user.player.save(update_fields=["last_answer_time", "num_completed_levels", "user_points"])

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
            messages.error(request, "lmfao ye kya likh rha hai bhai hasi aa gayi thodi sorry")
            return redirect('play', code=current_level)

@login_required(login_url='login')
def skip_level(request, code):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    num_completed_levels = current_user.player.num_completed_levels
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()
    completed_levels = user['completed_levels']
    completed_levels.append(code)
    new_countries_color = user['countries_color']
    new_countries_color[code] = 'green'
            
    user_doc.update({
        u'completed_levels': completed_levels,
        u'len_comp_levels': len(completed_levels),
        u'current_level': '',
        u'countries_color':new_countries_color,
    })

    num_completed_levels = len(completed_levels)
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
def levels(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if user['superuser']:
        levels = db.collection(u'levels').stream()
        database = db
        context = { 'levels': levels }
        return render(request, 'pages/admin_levels.html', context)

    return redirect('dashboard')

@login_required(login_url='login')
def level(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if user['superuser']:
        if request.method == "POST":
            level_id = request.POST['level_id'] 
            level = db.collection(u'levels').document(level_id).get().to_dict()
            context = {
                'level': level,
                'level_id':level_id,
            }
            return render(request, 'pages/admin_level.html', context)

    return redirect('dashboard')

@login_required(login_url='login')
def delete_level(request):
    if request.method == "POST":
        level_id = request.POST['level_id']
        db.collection(u'levels').document(level_id).delete()
        return redirect('levels')

@login_required(login_url='login')
def add_level(request):
    if request.method == "POST":
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
        })

        messages.error(request, "Level has been added.")
        return redirect('levels')

    return render(request, 'pages/add_level.html')

@login_required(login_url='login')
def logs(request):
    current_user = User.objects.get(id=request.user.id)
    username = current_user.username
    user_doc = db.collection(u'users').document(username)
    user = user_doc.get().to_dict()

    if user['superuser']:
        logs = db.collection(u'logs')
        logs = logs.order_by(u'timestamp', direction=firestore.Query.DESCENDING).stream()
        log_docs = list(log.to_dict() for log in logs)
        context = { 'log_docs': log_docs }
        return render(request, 'pages/logs.html', context)

    return redirect('dashboard')

def leaderboard(request):
    leaderboard = User.objects.filter(player__banned=False).order_by('-player__user_points', 'player__last_answer_time')
    context = { 'leaderboard': leaderboard }

    return render(request, 'pages/leaderboard.html', context)
