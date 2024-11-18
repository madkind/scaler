
def test_create_employee(employee_1, employee_2):
    pass

def test_create_manager(manager_1, manager_2):
    pass

def test_create_department(department_with_manager, department_without_manager):
    pass
    
def test_create_appointment(appointment):
    assert appointment.invitees.count() == 2