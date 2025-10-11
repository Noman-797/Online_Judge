from django.contrib import admin
from .models import Contest, ContestProblem, ContestParticipation, ContestAnnouncement


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'status', 'created_by']
    list_filter = ['start_time', 'end_time', 'created_by']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ContestProblem)
class ContestProblemAdmin(admin.ModelAdmin):
    list_display = ['contest', 'problem', 'order', 'points']
    list_filter = ['contest']


@admin.register(ContestParticipation)
class ContestParticipationAdmin(admin.ModelAdmin):
    list_display = ['contest', 'user', 'total_score', 'problems_solved', 'start_time']
    list_filter = ['contest', 'start_time']


@admin.register(ContestAnnouncement)
class ContestAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['contest', 'title', 'created_by', 'created_at']
    list_filter = ['contest', 'created_at']
    search_fields = ['title', 'message']