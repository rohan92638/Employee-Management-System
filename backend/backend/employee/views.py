from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from .models import Employee, Attendance, LeaveRequest, PerformanceRecord
from .serializers import EmployeeSerializer, AttendanceSerializer, LeaveRequestSerializer, PerformanceRecordSerializer
from .permissions import IsAdminOrManagerOrSelf
from rest_framework.permissions import AllowAny
import csv
import io
from rest_framework.parsers import MultiPartParser, FormParser



class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('department', 'user').all()
    serializer_class = EmployeeSerializer
    permission_classes= [IsAdminOrManagerOrSelf]
    # permission_classes = [AllowAny]   # change later if needed
    # authentication_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'employment_type', 'status']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'position']
    ordering_fields = ['first_name', 'last_name', 'date_of_joining', 'salary', 'created_at']
    parser_classes = (MultiPartParser, FormParser)

    # ✅ create employee (already works)
    def perform_create(self, serializer):
        user = self.request.user
        if user and user.is_authenticated:
            try:
                serializer.save(user=user)
            except Exception:
                serializer.save()
        else:
            serializer.save()

    # ✅ bulk delete all employees
    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all(self, request):
        count, _ = Employee.objects.all().delete()
        return Response({"message": f"{count} employees deleted."}, status=status.HTTP_200_OK)

    # ✅ export employees to CSV
    @action(detail=False, methods=['get'], url_path='export')
    def export_csv(self, request):
        qs = self.filter_queryset(self.get_queryset())
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        header = ['id', 'first_name', 'last_name', 'email', 'phone', 'department',
                  'position', 'date_of_joining', 'salary', 'employment_type', 'status']
        writer.writerow(header)
        for e in qs:
            writer.writerow([
                e.id, e.first_name, e.last_name, e.email, e.phone,
                getattr(e.department, 'name', '') if e.department else '',
                e.position, e.date_of_joining, e.salary, e.employment_type, e.status
            ])
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=employees_export.csv'
        return response

    # ✅ import employees from CSV
    @action(detail=False, methods=['post'], url_path='import',
            permission_classes=[IsAdminOrManagerOrSelf], parser_classes=[MultiPartParser, FormParser])
    #         permission_classes=[AllowAny],   # <--- change here
    # parser_classes=[MultiPartParser, FormParser])

    def import_csv(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = file.read().decode('utf-8')
            io_string = io.StringIO(decoded)
            reader = csv.DictReader(io_string)
            created = 0
            errors = []
            for idx, row in enumerate(reader, start=1):
                try:
                    emp, _ = Employee.objects.update_or_create(
                        email=row.get('email'),
                        defaults={
                            'first_name': row.get('first_name') or '',
                            'last_name': row.get('last_name') or '',
                            'phone': row.get('phone') or '',
                            'position': row.get('position') or '',
                        }
                    )
                    created += 1
                except Exception as e:
                    errors.append(f"Row {idx}: {str(e)}")
            return Response({"created": created, "errors": errors})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('employee').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrManagerOrSelf]
    # permission_classes = [AllowAny]   # change later if needed
    # authentication_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'date', 'status']
    search_fields = ['employee__first_name', 'employee__last_name']

    
class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee').all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAdminOrManagerOrSelf]
    # permission_classes = [AllowAny]   # change later if needed
    # authentication_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    
    
    @action(detail=True, methods=['post'], url_path='review')
    def review(self, request, pk=None):
        """
        Review a leave (approve/reject) — set status.
        Only Admin or Manager can review.
        body: {"action": "approve" / "reject"}
        """
        leave = self.get_object()
        action_ = request.data.get('action')
        if action_ not in ('approve', 'reject'):
            return Response({"detail": "Invalid action."}, status=400)
        if action_ == 'approve':
            leave.status = 'approved'
        else:
            leave.status = 'rejected'
        leave.reviewed_by = request.user
        # leave.reviewed_by = None
        leave.reviewed_at = timezone.now()
        leave.save()
        return Response(self.get_serializer(leave).data)
    
    


class PerformanceRecordViewSet(viewsets.ModelViewSet):
    queryset = PerformanceRecord.objects.select_related('employee').all()
    serializer_class = PerformanceRecordSerializer
    permission_classes = [IsAdminOrManagerOrSelf]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'review_date']
    search_fields = ['title', 'remarks', 'employee__first_name', 'employee__last_name']