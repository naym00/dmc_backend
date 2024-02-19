# serializers.py
from rest_framework import serializers
from .models import SyncInfoTable

class SyncInfoTableSerializer(serializers.ModelSerializer):
    syncTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = SyncInfoTable
        fields = '__all__'
