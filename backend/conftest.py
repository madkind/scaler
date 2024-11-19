from appointment.models import Appointment, AppointmentInvitee
import pytest
from rest_framework.test import APIClient
from human_resource.models import (
    Employee,
    EmployeeDepartmentAssignment,
    Department,
    Position,
)

def create_employee_to_department_assignment(employee, department):
    return EmployeeDepartmentAssignment.objects.create(
        employee=employee,
        department=department,
    )


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass


@pytest.fixture
def employee_1(department_with_manager):
    emp = Employee.objects.create(
        name="employee 1",
        email="first@employee.com",
        position=Position.EMPLOYEE.value,
    )
    create_employee_to_department_assignment(emp, department_with_manager)
    return emp 


@pytest.fixture
def employee_2(department_with_manager):
    emp = Employee.objects.create(
        name="employee 2",
        email="second@employee.com",
        position=Position.EMPLOYEE.value,
    )
    create_employee_to_department_assignment(emp, department_with_manager)
    return emp 


@pytest.fixture
def manager_1():
    emp = Employee.objects.create(
        name="manager 1",
        email="first@manager.com",
        position=Position.MANAGER.value,
    )
    return emp 


@pytest.fixture
def manager_2():
    emp = Employee.objects.create(
        name="manager 2",
        email="second@manager.com",
        position=Position.MANAGER.value,
    )
    return emp 


@pytest.fixture
def department_with_manager(manager_1):
    department = Department.objects.create(
        name="department_with_manager",
        description="department_with_manager",
    )
    department.manager = manager_1
    department.save()
    create_employee_to_department_assignment(manager_1, department)
    return department


@pytest.fixture
def department_without_manager():
    return Department.objects.create(
        name="department_without_manager", manager=None, description=None
    )


@pytest.fixture
def appointment(employee_1, employee_2):
    _appointment = Appointment.objects.create(
        start_datetime="2024-11-19T10:00:00Z",
        end_datetime="2024-11-19T11:00:00Z",
        title="Team Meeting",
        description="Weekly team sync",
        creator_id=employee_1.id,
    )

    AppointmentInvitee.objects.bulk_create(
        [
            AppointmentInvitee(appointment=_appointment, employee_id=employee_1.id),
            AppointmentInvitee(appointment=_appointment, employee_id=employee_2.id),
        ]
    )
    return _appointment

@pytest.fixture
def api_client():
    return APIClient()

