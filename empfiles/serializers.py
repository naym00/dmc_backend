from rest_framework import serializers
from .models import EmployeeFiles

class  EmploeeFileSerializer(serializers.ModelSerializer):
    class Meta :
        model= EmployeeFiles
        fields ='__all__'
