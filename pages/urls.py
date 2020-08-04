from django.urls import path
from . import views, auth, play, admin

urlpatterns = [
    path('', views.index, name="index"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('leaderboard', views.leaderboard, name="leaderboard"),
    path('finals', views.duel_leaderboard, name="duel_leaderboard"),
    path('why-am-i-banned', views.banned, name="banned"),

    path('login', auth.login, name="login"),
    path('logout', auth.logout, name="logout"),

    path('admin', admin.admin_dashboard, name="admin_dashboard"),
    path('admin/logs', admin.logs, name="logs"),
    path('admin/users', admin.users, name="users"),
    path('admin/users/user', admin.user, name="user"),
    path('admin/users/user/delete', admin.delete_user, name="delete_user"),
    path('admin/users/user/ban', admin.ban_user, name="ban_user"),
    path('admin/users/user/unban', admin.unban_user, name="unban_user"),
    path('admin/levels', admin.levels, name="levels"),
    path('admin/levels/level', admin.level, name="level"),
    path('admin/levels/add_level', admin.add_level, name="add_level"),
    path('admin/levels/level/delete', admin.delete_level, name="delete_level"),
    path('admin/levels/duel_level', admin.duel_level, name="duel_level"),
    path('admin/levels/add_duel_level', admin.add_duel_level, name="add_duel_level"),
    path('admin/levels/duel_level/delete' ,admin.delete_duel_level, name="delete_duel_level"),
]

# path('register', auth.register, name="register"),
# path('play/<str:code>/submit', play.submit, name="submit"),
# path('play/<str:code>/next', play.skip_level, name="skip_level"),
# path('play/<str:code>', views.play, name="play"),
# path('duel', play.play_duel, name="play_duel"),
# path('admin/assign-duels', admin.assign_duels, name="assign_duels"),
# path('wait-for-next-duel', views.waiting_page, name="waiting_page"),