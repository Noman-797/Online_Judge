from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    path('submit/<slug:slug>/', views.submit_solution, name='submit_solution'),
    path('test/<slug:slug>/', views.test_code, name='test_code'),
    path('ajax/<slug:slug>/', views.submit_ajax, name='submit_ajax'),
    path('detail/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('all/', views.all_submissions, name='all_submissions'),
    path('status/<int:submission_id>/', views.check_submission_status, name='check_status'),
    path('queue-status/', views.queue_status, name='queue_status'),
]