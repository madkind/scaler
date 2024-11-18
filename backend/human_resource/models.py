from django.db import models
from enum import Enum
from django.core.exceptions import ValidationError


class Position(Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    manager = models.OneToOneField(
        'Employee',
        on_delete=models.SET_NULL,
        related_name='manages_department',
        null=True,
        blank=True
    )
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.manager and self.manager.position != Position.MANAGER.value:
            raise ValidationError(f"The manager must have the position '{Position.MANAGER.value}'.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Employee(models.Model):
    class Position(models.TextChoices):
        EMPLOYEE = Position.EMPLOYEE.value, Position.EMPLOYEE.value
        MANAGER = Position.MANAGER.value, Position.MANAGER.value

    name = models.CharField(max_length=200)
    email = models.EmailField()
    position = models.CharField(max_length=10, choices=Position.choices)

    @property
    def department(self):
        assignment = getattr(self, 'department_assignment', None)
        return assignment.department if assignment else None
    
    def __str__(self):
        return f"{self.name} ({self.position})"


class EmployeeDepartmentAssignment(models.Model):
    employee = models.OneToOneField('Employee', unique=True, on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.employee.position != Position.EMPLOYEE.value:
            raise ValidationError(f"Only employees with the position '{Position.EMPLOYEE.value}' can be assigned.")
        super().save(*args, **kwargs)
