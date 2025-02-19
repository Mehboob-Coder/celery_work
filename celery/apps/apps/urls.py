from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from project2.views import TaskCategoryViewSet, TaskItemViewSet, TaskResultViewSet,Signup,Login,Logout
from rest_framework.authtoken.views import ObtainAuthToken

router = DefaultRouter()
router.register('categories', TaskCategoryViewSet)
router.register('tasks', TaskItemViewSet)
router.register('results', TaskResultViewSet)
router.register('signup',Signup,basename='signup')
router.register('login',Login,basename='login')
router.register('logout',Logout,basename='logout')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('gettoken/', ObtainAuthToken.as_view())
]
