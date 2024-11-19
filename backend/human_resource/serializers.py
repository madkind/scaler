from logging import Manager
from rest_framework import serializers
from .models import Department, Employee, EmployeeDepartmentAssignment
from django.db.models import Case, When, Value


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = (
            "id",
            "name",
            "email",
            "position",
            "department",
        )


class DepartmentSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.select_related(
            "employeedepartmentassignment__department"
        ).all(),
        pk_field=serializers.IntegerField(),
        allow_null=True,
    )

    class Meta:
        model = Department
        fields = (
            "id",
            "name",
            "manager",
            "description",
        )

    def validate(self, data):
        department_id = self.instance.id if self.instance else None
        manager = data.get("manager")
        if manager and department_id and manager.department.id != department_id:
            raise serializers.ValidationError(
                {"manager": ["Employee does not belong to this department."]}
            )
        return data

    def create(self, validated_data):
        instance = Department.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.manager = validated_data.get("manager")
        instance.save()
        self.appoint_manager(instance)
        return instance

    def appoint_manager(self, department_instance):
        manager_id = getattr(department_instance.manager, "id", None)
        # I keep track of the positions since you asked for it (as a field as I understood), but I would rather annotate it unless further requirements make it less viable.
        Employee.objects.filter(
            employeedepartmentassignment__department=department_instance.id
        ).update(
            position=Case(
                When(id=manager_id, then=Value(Employee.Position.MANAGER.value)),
                default=Value(Employee.Position.EMPLOYEE.value),
            )
        )
