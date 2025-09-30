from django.contrib import admin
from .models import Category, Problem, TestCase


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'created_by', 'is_active', 'created_at']
    list_filter = ['difficulty', 'category', 'is_active', 'created_at']
    search_fields = ['title', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TestCaseInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['problem', 'is_sample', 'created_at']
    list_filter = ['is_sample', 'created_at']
    search_fields = ['problem__title']