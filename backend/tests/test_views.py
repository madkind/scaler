import pytest
from rest_framework import status
from human_resource.models import Employee, Department
from appointment.models import Appointment

class TestEmployeeView:
    URL = "/api/employees/"

    def test_create_employee(self, api_client, department_with_manager):
        data = {
            "name": "Alice Johnson",
            "email": "alicejohnson@example.com",
            "position": Employee.Position.EMPLOYEE.value,
            "department": department_with_manager.id,
        }
        response = api_client.post(self.URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Alice Johnson"

    def test_change_department_for_employee(self, api_client, employee_1):
        new_department = Department.objects.create(
            name="Marketing", description="Marketing Department"
        )
        url = f"{self.URL}{employee_1.id}/"
        data = {
            "name": "employee 1",
            "email": "first@employee.com",
            "position": Employee.Position.EMPLOYEE.value,
            "department": new_department.id,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        # assert response.data["department"] == new_department.id # OLD value, no time
        employee_1.refresh_from_db()
        assert employee_1.department == new_department

    def test_list_employees(
        self, api_client, employee_1, employee_2, django_assert_num_queries
    ):
        with django_assert_num_queries(1):
            response = api_client.get(self.URL)
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data) >= 2
            assert any(employee["name"] == "employee 1" for employee in response.data)
            assert any(employee["name"] == "employee 2" for employee in response.data)

    def test_delete_employee(self, api_client, employee_1):
        url = f"{self.URL}{employee_1.id}/"
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Employee.objects.filter(id=employee_1.id).exists()

    @pytest.mark.parametrize(
        "filter,result_count",
        [
            ({"name": "bad"}, 0),
            ({"name": "emp"}, 2),
            ({"name": "1"}, 2),
            ({"name": "2"}, 1),
            ({"email": "bad"}, 0),
            ({"email": "emp"}, 2),
            ({"email": "first"}, 2),
            ({"email": "second"}, 1),
        ],
    )
    def test_list_employee_name_filter(
        self,
        api_client,
        manager_1,
        employee_1,
        employee_2,
        django_assert_num_queries,
        filter,
        result_count,
    ):
        with django_assert_num_queries(1):
            response = api_client.get(self.URL, filter)
            assert len(response.data) == result_count, response.data


class TestDepartmentView:
    URL = "/api/departments/"

    def test_create_department(self, api_client, department_with_manager):
        data = {
            "name": "Department name",
        }
        response = api_client.post(self.URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data["name"] == "Department name"

    def test_delete_department(self, api_client, department_with_manager):
        url = f"{self.URL}{department_with_manager.id}/"
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Department.objects.filter(id=department_with_manager.id).exists()

    # missing tests, no time

import pytest
from datetime import datetime
from rest_framework import status


@pytest.mark.django_db
class TestAppointmentViewSet:
    URL = '/api/appointments/'

    def test_list_appointments(self, api_client, appointment):
        response = api_client.get(self.URL)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == appointment.id
        assert response.data[0]['title'] == "Team Meeting"
    
    def test_retrieve_appointment(self, api_client, appointment):
        response = api_client.get(f'{self.URL}{appointment.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == appointment.id
        assert response.data['title'] == "Team Meeting"
        assert response.data['description'] == "Weekly team sync"
    
    def test_create_appointment(self, api_client, employee_1, employee_2):
        data = {
            "start_datetime": "2024-12-19T14:00:00Z",
            "end_datetime": "2024-12-19T15:00:00Z",
            "title": "New Meeting",
            "description": "Project discussion",
            "creator": employee_1.id,
            "invitees": [employee_1.id, employee_2.id]
        }
        
        response = api_client.post(self.URL, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == "New Meeting"
        assert len(response.data['invitees']) == 2
    
    def test_update_appointment(self, api_client, appointment):
        data = {
            "start_datetime": "2024-11-19T10:00:00Z",
            "end_datetime": "2024-11-19T11:00:00Z",
            "title": "Updated Meeting",
            "description": "Weekly team sync updated",
            "creator": appointment.creator_id,
            "invitees": [invitee.employee_id for invitee in appointment.appointment_invitees.all()]
        }
        
        response = api_client.put(f'{self.URL}{appointment.id}/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Updated Meeting"
        assert response.data['description'] == "Weekly team sync updated"
    
    def test_delete_appointment(self, api_client, appointment):
        response = api_client.delete(f'{self.URL}{appointment.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Appointment.objects.filter(id=appointment.id).exists()
    
    def test_filter_by_date(self, api_client, appointment):
        response = api_client.get(f'{self.URL}?date=2024-11-19')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == appointment.id
    
    def test_filter_by_invitee(self, api_client, appointment, employee_2):
        response = api_client.get(f'{self.URL}?invitee={employee_2.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == appointment.id
    
    def test_filter_by_date_and_invitee(self, api_client, appointment, employee_2):
        response = api_client.get(f'{self.URL}?date=2024-11-19&invitee={employee_2.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == appointment.id