from rest_framework import serializers
from .models import Appointment
from human_resource.models import Employee


class AppointmentSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    invitees = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), many=True
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "start_datetime",
            "end_datetime",
            "title",
            "description",
            "creator",
            "invitees",
        ]

    def validate(self, data):
        start_datetime = data["start_datetime"]
        end_datetime = data["end_datetime"]

        if start_datetime and end_datetime and start_datetime >= end_datetime:
            raise serializers.ValidationError(
                {"start_datetime": "Start datetime must be earlier than end datetime."}
            )

        return data
