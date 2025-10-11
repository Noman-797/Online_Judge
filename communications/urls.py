from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('send/', views.send_message, name='send_message'),
    path('check-unread/', views.check_unread_messages, name='check_unread_messages'),
    path('admin/', views.admin_messages, name='admin_messages'),
    path('admin/chat/<int:conversation_id>/', views.admin_chat_detail, name='admin_chat_detail'),
    path('admin/chat-data/<int:conversation_id>/', views.admin_chat_data, name='admin_chat_data'),
    path('admin/send/<int:conversation_id>/', views.admin_send_message, name='admin_send_message'),
    path('admin/delete/<int:conversation_id>/', views.admin_delete_chat, name='admin_delete_chat'),
    path('contest-announcements/check/', views.check_contest_announcements, name='check_contest_announcements'),
    path('contest-announcements/mark-viewed/<int:announcement_id>/', views.mark_contest_announcement_viewed, name='mark_contest_announcement_viewed'),
    path('clear-messages/', views.clear_messages, name='clear_messages'),
]