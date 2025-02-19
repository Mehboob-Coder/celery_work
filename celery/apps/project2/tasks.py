# from celery import shared_task
# from django.utils import timezone
# from .models import TaskItem, TaskResult
# import time
# from django_celery_beat.models import PeriodicTask
# from apps.celery import app


# @app.task(name='project2.tasks.process_task')
# def process_task(task_id):
#     task = None
#     start_processing_time = timezone.now()

#     try:
#         task = TaskItem.objects.get(id=task_id)

#         # Update to processing state
#         task.status = "PROCESSING"
#         task.updated_at = timezone.now()
#         task.save(update_fields=["status", "updated_at"])



#         # Calculate execution time from when processing started
#         # execution_time = (timezone.now() - start_processing_time).total_seconds()
#         # Complete task

#         if task.priority == 'NONE':
#             execution_time = (timezone.now() - task.scheduled_date).total_seconds()
#         else:
#             execution_time = (timezone.now() - task.created_at).total_seconds()

#         task.status = 'COMPLETED'
#         task.completed_at = timezone.now()
#         task.result = f'Task completed successfully at {timezone.now()}'
#         task.save()

#         # Create result
#         TaskResult.objects.create(
#             task=task,
#             output=f'Task processed for {execution_time:.2f} seconds',
#             execution_time=execution_time
#         )

#         return {
#             'status': 'success',
#             'task_id': task_id,
#             'execution_time': execution_time,
#             'processing_started': start_processing_time.isoformat(),
#             'processing_completed': timezone.now().isoformat()
#         }

#     except Exception as e:
#         if task:
#             task.status = 'FAILED'
#             task.result = f'Error: {str(e)}'
#             task.save()

#         return {'status': 'error', 'message': str(e)}

# @app.task
# def cleanup_old_tasks():
#     thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
#     TaskItem.objects.filter(created_at__lt=thirty_days_ago).delete()

# @app.task(name='project2.tasks.process_task')
# def revert_task_status(task_id):
#     try:
#         task = TaskItem.objects.get(id=task_id)
#         if task.status == "PROCESSING":
#             task.status = "PENDING"
#             task.updated_at = timezone.now()
#             task.save(update_fields=["status", "updated_at"])
#         return {'status': 'success', 'task_id': task_id, 'new_status': 'PENDING'}
#     except TaskItem.DoesNotExist:
#         return {'status': 'error', 'message': f'Task {task_id} not found'}


from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from .models import TaskItem, TaskResult
import json
from apps.celery import app

@app.task(name='project2.tasks.schedule_task')
def schedule_task(task_id):
    try:
        task = TaskItem.objects.get(id=task_id)

        if task.priority == 'NONE':
            # Create clocked schedule for scheduled date
            clocked_schedule, _ = ClockedSchedule.objects.get_or_create(
                clocked_time=task.scheduled_date
            )

            # Create periodic task
            PeriodicTask.objects.create(
                name=f"Task-{task.id}-{task.title}",
                task='project2.tasks.process_task',
                clocked=clocked_schedule,
                start_time=task.scheduled_date,
                args=json.dumps([task.id]),
                # enabled=True,
                # one_off=True,
            )

            # Schedule the task
            result = process_task.apply_async(
                args=[task.id],
                eta=task.scheduled_date
            )
            task.celery_task_id = result.id

        else:
            # Handle priority-based scheduling
            countdown_seconds = {
                'HIGH': 90,
                'MEDIUM': 160,
                'LOW': 190
            }.get(task.priority, 190)

            execution_time = timezone.now() + timezone.timedelta(seconds=countdown_seconds)

            # Create clocked schedule
            schedule, _ = ClockedSchedule.objects.get_or_create(
                clocked_time=execution_time
            )

            # Create periodic task
            PeriodicTask.objects.create(
                name=f"Task-{task.id}-{task.title}",
                task='project2.tasks.process_task',
                clocked=schedule,
                start_time=execution_time,
                args=json.dumps([task.id]),
                # enabled=True,
                # one_off=True,
            )

            # Schedule the task
            result = process_task.apply_async(
                args=[task.id],
                eta=execution_time
            )

            task.celery_task_id = result.id
            task.scheduled_date = execution_time

        task.save()

    except TaskItem.DoesNotExist:
        return {
            'status': 'error',
            'message': f'Task {task_id} not found'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


@app.task(name='project2.tasks.process_task')
def process_task(task_id):
    task = None
    start_processing_time = timezone.now()
    try:
        task = TaskItem.objects.get(id=task_id)

        # Update task status to "PROCESSING"
        task.status = "PROCESSING"
        task.updated_at = timezone.now()
        task.save(update_fields=["status", "updated_at"])

        # Calculate execution time based on task priority
        if task.priority == 'NONE':
            execution_time = (timezone.now() - task.scheduled_date).total_seconds()
        else:
            execution_time = (timezone.now() - task.created_at).total_seconds()

        # Complete the task
        task.status = 'COMPLETED'
        task.completed_at = timezone.now()
        task.result = f'Task completed successfully at {timezone.now()}'
        task.save()

        # Create a TaskResult to store execution details
        TaskResult.objects.create(
            task=task,
            output=f'Task processed for {execution_time:.2f} seconds',
            execution_time=execution_time
        )

        return {
            'status': 'success',
            'task_id': task_id,
            'execution_time': execution_time,
            'processing_started': start_processing_time.isoformat(),
            'processing_completed': timezone.now().isoformat()
        }

    except TaskItem.DoesNotExist:
        return {
            'status': 'error',
            'message': f'Task {task_id} not found'
        }

    except Exception as e:
        if task:
            task.status = 'FAILED'
            task.result = f'Error: {str(e)}'
            task.save()

        return {
            'status': 'error',
            'message': str(e)
        }


@app.task

def revert_task_status():
    try:
        five_minutes_ago = timezone.now() - timezone.timedelta(minutes=5)

        tasks = TaskItem.objects.filter(status="PROCESSING", updated_at__lt=five_minutes_ago)

        update_count = tasks.update(status="PENDING", updated_at=timezone.now())

    except Exception as e:
        return {
                'status': 'error',
                'message': str(e)
            }


@app.task
def cleanup_old_tasks():
    try:
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        deleted_count, _ = TaskItem.objects.filter(created_at__lt=thirty_days_ago).delete()

        return {
            'status': 'success',
            'deleted_count': deleted_count
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }