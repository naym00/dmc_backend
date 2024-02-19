from rest_framework import serializers

from .models import AttendanceReport

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model=AttendanceReport
        fields='__all__'
