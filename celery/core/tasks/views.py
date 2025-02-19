from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer
from .tasks import send_mail_task, process_data

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

@api_view(['POST'])
def trigger_mail_task(request):
    send_mail_task.delay()
    return Response({"message": "Mail task triggered"})

@api_view(['POST'])
def trigger_process_task(request):
    process_data.delay()
    return Response({"message": "Process task triggered"})
