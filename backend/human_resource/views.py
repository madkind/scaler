from rest_framework import viewsets
from .models import Employee, Department
from .serializers import EmployeeSerializer, DepartmentSerializer
import django_filters
from django_filters.rest_framework import DjangoFilterBackend


class EmployeeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Name"
    )
    email = django_filters.CharFilter(
        field_name="email", lookup_expr="icontains", label="Email"
    )

    class Meta:
        model = Employee
        fields = ["name", "email"]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related(
        "employeedepartmentassignment__department"
    ).all()
    serializer_class = EmployeeSerializer
    permission_classes = []
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EmployeeFilter


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = []
