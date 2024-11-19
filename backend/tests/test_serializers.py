from human_resource.serializers import DepartmentSerializer, EmployeeSerializer
from human_resource.models import Employee
from rest_framework import serializers
from conftest import create_employee_to_department_assignment
import pytest

class TestDepartmentSerializer:

    def test_serialize_department(self, department_with_manager, manager_1):
        serializer = DepartmentSerializer(department_with_manager)
        assert serializer.data["name"] == department_with_manager.name
        assert serializer.data["description"] == department_with_manager.description
        assert serializer.data["manager"] == manager_1.id

    def test_create_department_without_manager(self):
        data = {
            "name": "New Department",
            "description": "New Description",
            "manager": None,
        }        
        serializer = DepartmentSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        
        department = serializer.save()

        assert department.name == "New Department"
        assert department.description == "New Description"
        assert department.manager is None

    def test_update_department_with_manager(self, department_without_manager, manager_2):
        create_employee_to_department_assignment(manager_2, department_without_manager)
        data = {
            "id": department_without_manager.id,
            "manager": manager_2.id,
        }        
        serializer = DepartmentSerializer(data=data, partial=True)
        assert serializer.is_valid(raise_exception=True)
        
        department = serializer.save()

        assert department.manager == manager_2
        
    def test_update_department_with_manager_fails_due_department_diff(self, department_without_manager, manager_1):
        assert manager_1.department is None
        data = {
            "id": department_without_manager.id,
            "manager": manager_1.id,
        }        
        serializer = DepartmentSerializer(instance=department_without_manager, data=data, partial=True)
        
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
            assert exc_info.value.detail == {
                "manager": ["Employee does not belong to this department."]
            }
        
    def test_update_department_when_new_manager_is_appointed_old_manager_is_demoted(self, department_with_manager, manager_1, employee_1):
        assert manager_1.department == department_with_manager
        assert manager_1.position == Employee.Position.MANAGER.value

        data = {
            "id": department_with_manager.id,
            "manager": employee_1.id,
        }        
        serializer = DepartmentSerializer(instance=department_with_manager, data=data, partial=True)
        assert serializer.is_valid(raise_exception=True)
        serializer.save()

        manager_1.refresh_from_db()
        employee_1.refresh_from_db()
        assert manager_1.position == Employee.Position.EMPLOYEE.value
        assert employee_1.position == Employee.Position.MANAGER.value

class TestEmployeeSerializer:

    def test_serialize_department(self, employee_1):
        serializer = EmployeeSerializer(employee_1)
        assert serializer.data["id"] == employee_1.id
        assert serializer.data["name"] == employee_1.name
        assert serializer.data["email"] == employee_1.email
        assert serializer.data["position"] == employee_1.position
        assert serializer.data["department"] == employee_1.department
        
    # skipping rest of tests since no custom logic is implemented
