from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import TaskViewSet, trigger_mail_task, trigger_process_task

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/trigger-mail/', trigger_mail_task),
    path('api/trigger-process/', trigger_process_task),
]
