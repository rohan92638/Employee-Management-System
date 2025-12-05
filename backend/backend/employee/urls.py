from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'emp', views.EmployeeViewSet, basename='employee')
router.register(r'attendances', views.AttendanceViewSet, basename='attendance')
router.register(r'leaves', views.LeaveRequestViewSet, basename='leaverequest')
router.register(r'performance', views.PerformanceRecordViewSet, basename='performance')

urlpatterns = [
    path('', include(router.urls)),
]
