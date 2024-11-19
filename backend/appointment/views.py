from rest_framework import viewsets
from django_filters import rest_framework as filters
from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentFilter(filters.FilterSet):
    date = filters.DateFilter(field_name='start_datetime__date')
    invitee = filters.NumberFilter(field_name='invitees')

    class Meta:
        model = Appointment
        fields = ['date', 'invitee']


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by('start_datetime')
    serializer_class = AppointmentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AppointmentFilter