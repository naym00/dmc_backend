from .models import StructuredLog
from rest_framework import serializers

class StructuredLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StructuredLog
        fields='__all__'
        