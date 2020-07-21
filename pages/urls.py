from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login, name="login"),
    path('register', views.register, name="register"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('logout', views.logout, name="logout"),
    path('play/<str:code>', views.play, name="play"),
    path('play/<str:code>/submit', views.submit, name="submit"),
    path('why-am-i-banned', views.banned, name="banned"),
    path('admin_dashboard', views.admin_dashboard, name="admin_dashboard"),
    path('admin_dashboard/users',views.users,name="users"),
    path('admin_dashboard/users/user',views.user,name="user"),
    path('admin_dashboard/users/user/delete',views.delete_user,name="delete_user"),
    path('admin_dashboard/users/user/ban',views.ban_user,name="ban_user"),
    path('admin_dashboard/users/user/unban',views.unban_user,name="unban_user"),
]