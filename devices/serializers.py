from rest_framework import serializers
from .models import Devices

class DevicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields ='__all__'
        