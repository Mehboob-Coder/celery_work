from django.contrib import admin
from .models import TaskCategory, TaskItem, TaskResult,User
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# Register your models here.
@admin.register(User)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [ 'username', 'email','password','phone','profile_pic', 'file','Reg_id']

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(TaskItem)
class TaskItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'user', 'status', 'priority', 'created_at','scheduled_date')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')
    readonly_fields = ('celery_task_id', 'completed_at')

@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ('task', 'execution_time', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('task__title', 'output', 'error')

# admin.site.register(IntervalSchedule)
# admin.site.register(PeriodicTask)