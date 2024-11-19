from django.db import models
from human_resource.models import Employee


class Appointment(models.Model):
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    creator = models.OneToOneField(Employee, on_delete=models.CASCADE)
    invitees = models.ManyToManyField(
        Employee,
        through='AppointmentInvitee',
        related_name='appointments'
    )
    def __str__(self):
        return self.title

class AppointmentInvitee(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='appointment_invitees'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='appointment_invitations'
    )
    
    class Meta:
        unique_together = ['appointment', 'employee']