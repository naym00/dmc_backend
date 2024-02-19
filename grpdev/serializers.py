from rest_framework import serializers
from .models import GroupDevice
class GroupDeviceSerializer(serializers.ModelSerializer):
    class  Meta:
        model =GroupDevice
        fields='__all__'
        