from rest_framework import serializers
from .models import Employee, Attendance, LeaveRequest, PerformanceRecord


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['id']
        

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['id', 'status', 'created_at', 'reviewed_by', 'reviewed_at']
        

class PerformanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
        
        
class EmployeeSerializer(serializers.ModelSerializer):
    attendances = AttendanceSerializer(many=True, read_only=True)
    leave_requests = LeaveRequestSerializer(many=True, read_only=True)
    performance_records = PerformanceRecordSerializer(many=True, read_only=True)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model= Employee
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'phone', 'department',
            'position', 'date_of_joining', 'salary', 'employment_type', 'profile_picture',
            'profile_picture_url', 'status', 'created_at', 'updated_at',
            'attendances', 'leave_requests', 'performance_records'
        ]
        
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            url = obj.profile_picture.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        # Return URL to a default avatar if desired
        return None