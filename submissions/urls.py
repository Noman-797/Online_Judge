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
    path('check/<int:submission_id>/', views.check_submission_status, name='check_status'),
    path('recent-submissions/', views.recent_submissions, name='recent_submissions'),
    path('process-queue/', views.process_queue_manual, name='process_queue_manual'),
    path('queue-api/', views.queue_status_api, name='queue_status_api'),
    path('check-pending/', views.check_pending_submissions, name='check_pending'),
    path('status/<int:submission_id>/', views.submission_status_api, name='submission_status_api'),
    path('api/problem-verdicts/', views.problem_verdicts_api, name='problem_verdicts_api'),
]