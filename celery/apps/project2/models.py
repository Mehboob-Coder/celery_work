from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    email=models.EmailField(unique=True, blank=True,null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True,null=True)
    file=models.FileField(upload_to='files', blank=True,null=True)
    Reg_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class TaskCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Task Categories"

class TaskItem(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )

    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('NONE', 'None'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NONE')
    celery_task_id = models.CharField(max_length=100, unique=True, null=True)
    result = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.title

class TaskResult(models.Model):
    task = models.ForeignKey(TaskItem, on_delete=models.CASCADE)
    output = models.TextField()
    error = models.TextField(null=True, blank=True)
    execution_time = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.task.title}"
