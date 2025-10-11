from django.urls import path
from . import views

app_name = 'problems'

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('<slug:slug>/', views.problem_solve, name='problem_solve'),
    path('detail/<slug:slug>/', views.problem_detail, name='problem_detail'),

    path('admin/problems/', views.admin_problems, name='admin_problems'),
    path('admin/add/', views.add_problem, name='add_problem'),
    path('admin/<slug:slug>/edit/', views.edit_problem, name='edit_problem'),
    path('admin/<slug:slug>/test-cases/', views.manage_test_cases, name='manage_test_cases'),
    path('admin/test-case/<int:test_case_id>/edit/', views.edit_test_case, name='edit_test_case'),
    path('admin/test-case/<int:test_case_id>/delete/', views.delete_test_case, name='delete_test_case'),
    path('admin/categories/', views.manage_categories, name='manage_categories'),
    path('admin/categories/add/', views.add_category, name='add_category'),
    path('admin/categories/<int:id>/edit/', views.edit_category, name='edit_category'),
    path('admin/categories/<int:id>/delete/', views.delete_category, name='delete_category'),
    path('admin/<slug:slug>/delete/', views.delete_problem, name='delete_problem'),
]