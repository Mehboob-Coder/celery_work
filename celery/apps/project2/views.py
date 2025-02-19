from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TaskCategory, TaskItem, TaskResult,User
from .serializers  import TaskCategorySerializer, TaskItemSerializer, TaskStatusSerializer, TaskResultSerializer, UserSerializer
from .tasks import process_task
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from .tasks import schedule_task, revert_task_status
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django_celery_beat.models import ClockedSchedule,PeriodicTask
# Create your views here.
class Signup(viewsets.ViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)  
        return Response(serializer.errors)

    
class Login(viewsets.ViewSet):
    """This class handle login functionality
    login with username and password or email and password"""
    permission_classes = [AllowAny]

    def create(self, request):
        username_or_email = request.data.get("username")
        password = request.data.get("password")

        user_query = User.objects.filter(Q(username=username_or_email) | Q(email=username_or_email)).first()
        user = None
        if user_query:
            user = authenticate(username=user_query.username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response(
                    {
                        "token": token.key,
                        "message": "Login successful.",
                        
                        "user_data":serializer.data,
                        
                    },
                    status=status.HTTP_200_OK,
                )

        return Response(
            {"error": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class Logout(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def create(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully."})

class TaskCategoryViewSet(viewsets.ModelViewSet):
    queryset = TaskCategory.objects.all()
    serializer_class = TaskCategorySerializer

# class TaskItemViewSet(viewsets.ModelViewSet):
#     queryset = TaskItem.objects.all()
#     serializer_class = TaskItemSerializer
#
#
#     # def perform_create(self, serializer):
#     #
#     #     task = serializer.save(user=self.request.user)
#     #
#     #     if task.priority == 'NONE':
#     #         # Create clocked schedule for scheduled date
#     #         clocked_schedule = ClockedSchedule.objects.create(
#     #             clocked_time=task.scheduled_date
#     #         )
#     #
#     #         # Create periodic task
#     #         periodic_task = PeriodicTask.objects.create(
#     #             name=f"Task-{task.id}-{task.title}",
#     #             task='project2.tasks.process_task',
#     #             clocked=clocked_schedule,
#     #             start_time=task.scheduled_date,
#     #             args=[task.id],
#     #             enabled=True,
#     #             one_off=True,
#     #
#     #         )
#     #
#     #         # Schedule the task
#     #         result = process_task.apply_async(
#     #             args=[task.id],
#     #             eta=task.scheduled_date
#     #         )
#     #         task.celery_task_id = result.id
#     #
#     #
#     #     else:
#     #         # Handle priority-based scheduling
#     #         countdown_seconds = {
#     #             'HIGH': 90,
#     #             'MEDIUM': 160,
#     #             'LOW': 190
#     #         }.get(task.priority, 190)
#     #
#     #         execution_time = timezone.now() + timezone.timedelta(seconds=countdown_seconds)
#     #
#     #         # Create clocked schedule
#     #         schedule = ClockedSchedule.objects.create(
#     #             clocked_time=execution_time
#     #         )
#     #
#     #         # schedule = IntervalSchedule.objects.create(
#     #         #     every=countdown_seconds,
#     #         #     period=IntervalSchedule.SECONDS,
#     #         # )
#     #
#     #         # Create periodic task
#     #         periodic_task = PeriodicTask.objects.create(
#     #             name=f"Task-{task.id}-{task.title}",
#     #             task='project2.tasks.process_task',
#     #             clocked=schedule,
#     #             start_time=execution_time,
#     #             args=[task.id],
#     #             enabled=True,
#     #             one_off=True,
#     #         )
#     #
#     #         # Schedule the task
#     #         result = process_task.apply_async(
#     #             args=[task.id],
#     #             eta=execution_time
#     #         )
#     #
#     #         task.celery_task_id = result.id
#     #         task.scheduled_date = execution_time
#     #
#     #     task.save()
#     #
#
#     def perform_create(self, serializer):
#         task = serializer.save(user=self.request.user)  # Save user in one go
#
#         if task.status == "PROCESSING":
#             # Schedule status change to PENDING after 5 minutes
#             execution_time = timezone.now() + timezone.timedelta(minutes=5)
#             clocked_schedule, _ = ClockedSchedule.objects.get_or_create(clocked_time=execution_time)
#             PeriodicTask.objects.create(
#                 name=f"Revert-Task-{task.id}",
#                 task='project2.tasks.revert_task_status',
#                 clocked=clocked_schedule,
#                 start_time=execution_time,
#                 args=json.dumps([task.id]),
#                 enabled=True,
#                 one_off=True,
#             )
#
#         if task.priority == 'NONE':
#             # Create clocked schedule for scheduled date
#             clocked_schedule = ClockedSchedule.objects.create(
#                 clocked_time=task.scheduled_date
#             )
#
#             # Create periodic task
#             periodic_task = PeriodicTask.objects.create(
#                 name=f"Task-{task.id}-{task.title}",
#                 task='project2.tasks.process_task',
#                 clocked=clocked_schedule,
#                 start_time=task.scheduled_date,
#                 args=[task.id],
#                 enabled=True,
#                 one_off=True,
#             )
#
#             # Schedule the task
#             result = process_task.apply_async(
#                 args=[task.id],
#                 eta=task.scheduled_date
#             )
#             task.celery_task_id = result.id
#
#         else:
#             # Handle priority-based scheduling
#             countdown_seconds = {
#                 'HIGH': 90,
#                 'MEDIUM': 160,
#                 'LOW': 190
#             }.get(task.priority, 190)
#
#             execution_time = timezone.now() + timezone.timedelta(seconds=countdown_seconds)
#
#             # Create clocked schedule
#             schedule = ClockedSchedule.objects.create(
#                 clocked_time=execution_time
#             )
#
#             # Create periodic task
#             periodic_task = PeriodicTask.objects.create(
#                 name=f"Task-{task.id}-{task.title}",
#                 task='project2.tasks.process_task',
#                 clocked=schedule,
#                 start_time=execution_time,
#                 args=[task.id],
#                 enabled=True,
#                 one_off=True,
#             )
#
#             # Schedule the task
#             result = process_task.apply_async(
#                 args=[task.id],
#                 eta=execution_time
#             )
#
#             task.celery_task_id = result.id
#             task.scheduled_date = execution_time
#
#         task.save()
#
#     @action(detail=True, methods=['get'])
#     def status(self, request, pk=None):
#         task = self.get_object()
#         processing_time = None
#         if task.completed_at and task.created_at:
#             processing_time = (task.completed_at - task.created_at).total_seconds()
#
#         # Get periodic task info
#         from django_celery_beat.models import PeriodicTask
#         periodic_task = PeriodicTask.objects.filter(name__contains=f"Task-{task.id}").first()
#
#         response_data = {
#             'task_id': task.celery_task_id,
#             'status': task.status,
#             'result': task.result,
#             'created_at': task.created_at,
#             'completed_at': task.completed_at,
#             'processing_time': processing_time,
#             'periodic_task': {
#                 'name': periodic_task.name if periodic_task else None,
#                 'schedule': str(periodic_task.interval) if periodic_task else None,
#                 'last_run': periodic_task.last_run_at if periodic_task else None,
#                 'enabled': periodic_task.enabled if periodic_task else False
#             }
#         }
#         return Response(response_data)
#

class TaskItemViewSet(viewsets.ModelViewSet):
    queryset = TaskItem.objects.all()
    serializer_class = TaskItemSerializer

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)

        # Schedule the task based on priority or scheduled date
        schedule_task.delay(task.id)


    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        task = self.get_object()
        processing_time = None
        if task.completed_at and task.created_at:
            processing_time = (task.completed_at - task.created_at).total_seconds()

        # Get periodic task info
        from django_celery_beat.models import PeriodicTask
        periodic_task = PeriodicTask.objects.filter(name__contains=f"Task-{task.id}").first()

        response_data = {
            'task_id': task.celery_task_id,
            'status': task.status,
            'result': task.result,
            'created_at': task.created_at,
            'completed_at': task.completed_at,
            'processing_time': processing_time,
            'periodic_task': {
                'name': periodic_task.name if periodic_task else None,
                'schedule': str(periodic_task.interval) if periodic_task else None,
                'last_run': periodic_task.last_run_at if periodic_task else None,
                'enabled': periodic_task.enabled if periodic_task else False
            }
        }
        return Response(response_data)

class TaskResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer

