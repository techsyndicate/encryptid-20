  
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login, name="login"),
    path('register', views.register, name="register"),
    path('play', views.dashboard, name="dashboard"),
    path('logout', views.logout, name="logout"),
    path('country/<str:code>/',views.level_call,name="level_call"),
]