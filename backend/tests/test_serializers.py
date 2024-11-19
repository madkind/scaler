from appointment.serializers import AppointmentSerializer
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

    def test_update_department_with_manager(
        self, department_without_manager, manager_2
    ):
        create_employee_to_department_assignment(manager_2, department_without_manager)
        data = {
            "id": department_without_manager.id,
            "manager": manager_2.id,
        }
        serializer = DepartmentSerializer(data=data, partial=True)
        assert serializer.is_valid(raise_exception=True)

        department = serializer.save()

        assert department.manager == manager_2

    def test_update_department_with_manager_fails_due_department_diff(
        self, department_without_manager, manager_1
    ):
        assert manager_1.department is None
        data = {
            "id": department_without_manager.id,
            "manager": manager_1.id,
        }
        serializer = DepartmentSerializer(
            instance=department_without_manager, data=data, partial=True
        )

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert exc_info.value.detail == {
            "manager": ["Employee does not belong to this department."]
        }

    def test_update_department_when_new_manager_is_appointed_old_manager_is_demoted(
        self, department_with_manager, manager_1, employee_1
    ):
        assert manager_1.department == department_with_manager
        assert manager_1.position == Employee.Position.MANAGER.value

        data = {
            "id": department_with_manager.id,
            "manager": employee_1.id,
        }
        serializer = DepartmentSerializer(
            instance=department_with_manager, data=data, partial=True
        )
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
        assert serializer.data["department"] == employee_1.department.id

    def test_create_employee(self, department_with_manager):
        data = {
            "name": "NAME",
            "email": "electronic@mail.com",
            "position": Employee.Position.EMPLOYEE.value,
            "department": department_with_manager.id,
        }

        serializer = EmployeeSerializer(data=data)
        assert serializer.is_valid(raise_exception=True)
        employee = serializer.save()

        assert employee.name == data["name"]
        assert employee.email == data["email"]
        assert employee.department.id == data["department"]

    def test_update_employee_can_change_department(
        self, employee_1, department_with_manager, department_without_manager
    ):
        assert employee_1.department == department_with_manager
        data = {
            "name": "NAME",
            "email": "electronic@mail.com",
            "position": Employee.Position.EMPLOYEE.value,
            "department": department_without_manager.id,
        }

        serializer = EmployeeSerializer(data=data, instance=employee_1)
        assert serializer.is_valid(raise_exception=True)
        serializer.save()

        employee_1.refresh_from_db()
        assert employee_1.department == department_without_manager

    def test_update_employee_with_manager_position_can_NOT_change_department(
        self, manager_1, department_with_manager, department_without_manager
    ):
        assert manager_1.department == department_with_manager
        data = {
            "name": "NAME",
            "email": "electronic@mail.com",
            "position": Employee.Position.EMPLOYEE.value,
            "department": department_without_manager.id,
        }

        serializer = EmployeeSerializer(data=data, instance=manager_1)

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert exc_info.value.detail == {
            "department": [
                "Managers can not change department. Please demote manager to employee position, then try again!"
            ]
        }


class TestAppointmentSerializer:

    def test_serialize_appointment(self, appointment, employee_1, employee_2):
        serializer = AppointmentSerializer(instance=appointment)
        assert serializer.data["title"] == "Team Meeting"
        assert serializer.data["description"] == "Weekly team sync"
        assert serializer.data["creator"] == employee_1.id
        assert serializer.data["invitees"] == [employee_1.id, employee_2.id]

    def test_appointment_create(self, employee_1, employee_2):
        data = {
            "start_datetime": "2024-11-19T10:00:00Z",
            "end_datetime": "2024-11-19T11:00:00Z",
            "title": "Team Meeting",
            "description": "Weekly team sync",
            "creator": employee_1.id,
            "invitees": [employee_1.id, employee_2.id],
        }

        serializer = AppointmentSerializer(data=data)

        assert serializer.is_valid(raise_exception=True)
        appointment_obj = serializer.save()

        assert appointment_obj.title == "Team Meeting"
        assert appointment_obj.description == "Weekly team sync"
        assert appointment_obj.creator == employee_1

        invitees = appointment_obj.invitees.all()
        assert invitees.count() == 2
        assert set(invitee.id for invitee in invitees) == {employee_1.id, employee_2.id}

    def test_appointment_serializer_end_before_start(self, employee_1):
        invalid_data = {
            "start_datetime": "2024-11-19T11:00:00Z",
            "end_datetime": "2024-11-19T10:00:00Z",
            "title": "Team Meeting",
            "description": "Weekly team sync",
            "creator": employee_1.id,
            "invitees": [employee_1.id],
        }

        serializer = AppointmentSerializer(data=invalid_data)

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert exc_info.value.detail == {
            "start_datetime": ["Start datetime must be earlier than end datetime."]
        }

    def test_appointment_remove_invitee(self, appointment, employee_1):
        data = {
            "start_datetime": "2024-11-19T10:00:00Z",
            "end_datetime": "2024-11-19T11:00:00Z",
            "title": "Team Meeting",
            "description": "Weekly team sync",
            "creator": employee_1.id,
            "invitees": [employee_1.id],
        }
        serializer = AppointmentSerializer(instance=appointment, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        assert appointment.invitees.count() == 1
        assert appointment.invitees.get() == employee_1
        

