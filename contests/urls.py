from django.urls import path
from . import views

app_name = 'contests'

urlpatterns = [
    path('', views.contest_list, name='contest_list'),
    path('<slug:slug>/', views.contest_detail, name='contest_detail'),
    path('<slug:slug>/problems/', views.contest_problems, name='contest_problems'),
    path('<slug:slug>/join/', views.join_contest, name='join_contest'),
    path('<slug:slug>/leaderboard/', views.contest_leaderboard, name='leaderboard'),
    path('admin/contests/', views.admin_contests, name='admin_contests'),
    path('admin/add/', views.add_contest, name='add_contest'),
    path('admin/<slug:slug>/problems/', views.manage_contest_problems, name='manage_problems'),
    path('admin/<slug:slug>/problems/<int:problem_id>/remove/', views.remove_contest_problem, name='remove_problem'),
    path('admin/<slug:slug>/edit/', views.edit_contest, name='edit_contest'),
    path('admin/<slug:slug>/delete/', views.delete_contest, name='delete_contest'),
    path('admin/<slug:slug>/monitor/', views.monitor_contest, name='monitor_contest'),
    path('admin/submission/<int:submission_id>/code/', views.view_submission_code, name='view_code'),
    path('admin/<slug:slug>/ban/<int:user_id>/', views.ban_participant, name='ban_participant'),
    path('admin/<slug:slug>/unban/<int:user_id>/', views.unban_participant, name='unban_participant'),
    path('admin/<slug:slug>/user/<int:user_id>/submissions/', views.user_submissions, name='user_submissions'),
]