from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department
from .serializers import DepartmentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('id')   # ascending order
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated] # you can adjust
    # permission_classes = [AllowAny]  # anyone can access
    # authentication_classes = []  # 👈 Remove all authentication
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location']
    search_fields = ['name', 'manager_name', 'description']
    ordering_fields = ['name', 'created_at']
