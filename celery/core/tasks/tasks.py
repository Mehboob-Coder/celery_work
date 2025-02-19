from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime
from .models import Task

@shared_task
def send_mail_task():
    send_mail(
        'Celery Task',
        'This is a test email from Celery.',
        'from@example.com',
        ['to@example.com'],
        fail_silently=False,
    )
    return "Mail Sent Successfully"

@shared_task
def process_data():
    task = Task.objects.create(
        title=f"Task created at {datetime.now()}",
        status="completed",
        completed_at=datetime.now()
    )
    return f"Task {task.id} created successfully"
