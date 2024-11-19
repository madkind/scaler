import pytest
from rest_framework import status
from human_resource.models import Employee, Department


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
        url = f"/api/employees/{employee_1.id}/"
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Employee.objects.count() == 0

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
