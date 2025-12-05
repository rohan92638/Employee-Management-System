from django.contrib import admin
from .models import Employee, Attendance, LeaveRequest, PerformanceRecord

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'department', 'position', 'status')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('status', 'employment_type', 'department')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'time_in', 'time_out')
    list_filter = ('status', 'date')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'status')
    list_filter = ('status',)


@admin.register(PerformanceRecord)
class PerformanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'review_date', 'score')
