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
    path('play/<str:code>/skip', views.skip_level, name="skip_level"),
    path('why-am-i-banned', views.banned, name="banned"),
    path('admin', views.admin_dashboard, name="admin_dashboard"),
    path('admin/users',views.users,name="users"),
    path('admin/users/user',views.user,name="user"),
    path('admin/users/user/delete',views.delete_user,name="delete_user"),
    path('admin/users/user/ban',views.ban_user,name="ban_user"),
    path('admin/users/user/unban',views.unban_user,name="unban_user"),
    path('admin/levels',views.levels,name="levels"),
    path('admin/levels/level',views.level,name="level"),
    path('admin/levels/level/delete',views.delete_level,name="delete_level"),
    path('admin/levels/add_level',views.add_level,name="add_level"),
    path('admin/logs',views.logs,name="logs"),
]