from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Max
from django.contrib.admin.views.decorators import staff_member_required
from .models import Conversation, Message
from django.utils import timezone
from contests.models import ContestAnnouncement


@login_required
def chat_list(request):
    # Get user's conversations with admins (exclude hidden)
    conversations = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants__is_staff=True
    ).exclude(
        hidden_for=request.user
    ).prefetch_related('messages__sender').order_by('-updated_at')
    
    # Mark messages as read for regular users
    if not request.user.is_staff:
        Message.objects.filter(
            conversation__participants=request.user,
            sender__is_staff=True,
            is_read=False
        ).update(is_read=True)
    
    return render(request, 'communications/chat_list.html', {
        'conversations': conversations
    })


@login_required
def chat_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    # Mark messages as read
    conversation.messages.filter(is_read=False).exclude(
        sender=request.user
    ).update(is_read=True)
    
    # Get messages
    messages = conversation.messages.order_by('created_at')
    other_user = conversation.get_other_user(request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            return redirect('communications:chat_detail', conversation_id=conversation_id)
    
    return render(request, 'communications/chat_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user
    })


@login_required
def send_message(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            # Get or create conversation with any admin
            admin = User.objects.filter(is_staff=True).first()
            if admin:
                conversation = Conversation.objects.filter(
                    participants=request.user
                ).filter(
                    participants=admin
                ).first()
                
                if not conversation:
                    conversation = Conversation.objects.create()
                    conversation.participants.add(request.user, admin)
                
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content=content
                )
                conversation.save()  # Update timestamp
    
    return redirect('communications:chat_list')


@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    users = []
    
    if query and len(query) >= 2:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query),
            is_staff=True
        ).exclude(id=request.user.id)[:10]
    
    return JsonResponse({
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'name': user.get_full_name() or user.username,
                'is_staff': user.is_staff
            }
            for user in users
        ]
    })


@login_required
def check_unread_messages(request):
    if request.user.is_staff:
        # For admin: count all unread messages from non-staff users
        unread_count = Message.objects.filter(
            conversation__participants=request.user,
            sender__is_staff=False,
            is_read=False
        ).count()
    else:
        # For regular users: count unread messages from staff
        unread_count = Message.objects.filter(
            conversation__participants=request.user,
            sender__is_staff=True,
            is_read=False
        ).count()
    
    return JsonResponse({'unread_count': unread_count})


@staff_member_required
def admin_messages(request):
    conversations = Conversation.objects.all().prefetch_related(
        'participants', 'messages__sender'
    ).order_by('-updated_at')
    
    # Add unread status to conversations
    for conversation in conversations:
        conversation.has_unread = conversation.messages.filter(
            sender__is_staff=False, is_read=False
        ).exists()
    
    # Mark all messages as read for admin
    Message.objects.filter(
        sender__is_staff=False,
        is_read=False
    ).update(is_read=True)
    
    return render(request, 'communications/admin_messages.html', {
        'conversations': conversations
    })


@staff_member_required
def admin_chat_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            return redirect('communications:admin_chat_detail', conversation_id=conversation_id)
    
    messages = conversation.messages.order_by('created_at')
    other_user = conversation.get_other_user(request.user)
    
    return render(request, 'communications/admin_chat_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user
    })


@staff_member_required
def admin_chat_data(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = conversation.messages.order_by('created_at')
    
    return JsonResponse({
        'messages': [{
            'content': msg.content,
            'is_admin': msg.sender.is_staff,
            'time': msg.created_at.strftime('%g:%i %p')
        } for msg in messages]
    })


@staff_member_required
def admin_send_message(request, conversation_id):
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id)
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
    return redirect('communications:admin_messages')


@staff_member_required
def admin_delete_chat(request, conversation_id):
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, id=conversation_id)
        conversation.delete()
        messages.success(request, 'Chat deleted successfully!')
        return redirect('communications:admin_messages')
    return redirect('communications:admin_messages')


@login_required
def check_contest_announcements(request):
    from datetime import timedelta
    recent_time = timezone.now() - timedelta(hours=24)
    
    recent_announcements = ContestAnnouncement.objects.filter(
        created_at__gte=recent_time
    ).select_related('contest').order_by('-created_at')
    
    seen_announcements = request.session.get('seen_announcements', [])
    
    new_announcements = []
    for announcement in recent_announcements:
        if announcement.id not in seen_announcements:
            new_announcements.append({
                'id': announcement.id,
                'title': announcement.title,
                'message': announcement.message,
                'contest': announcement.contest.title
            })
    
    return JsonResponse({
        'announcements': new_announcements
    })


@login_required
def mark_contest_announcement_viewed(request, announcement_id):
    if request.method == 'POST':
        seen_announcements = request.session.get('seen_announcements', [])
        if announcement_id not in seen_announcements:
            seen_announcements.append(announcement_id)
            request.session['seen_announcements'] = seen_announcements
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'})


@login_required
def clear_messages(request):
    if request.method == 'POST':
        conversations = Conversation.objects.filter(participants=request.user)
        for conv in conversations:
            conv.hidden_for.add(request.user)
        messages.success(request, 'All messages cleared successfully!')
        return redirect('communications:chat_list')
    return redirect('communications:chat_list')