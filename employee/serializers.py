from rest_framework import serializers
from .models import Employee, EmployeeGroupDevice,TrainEmployeeFromCSV

class EmployeeSerializer(serializers.ModelSerializer):
    # image_url = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    # def get_image_url(self, obj):
    #     # Use get() to avoid KeyError
    #     request = self.context.get('request')
    #     if request and obj.image_location:
    #         return request.build_absolute_uri(obj.image_location)
    #     return None

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     # If image_url is present, set image_location to its value
    #     if 'image_url' in data:
    #         data['image_location'] = data['image_url']
    #         del data['image_url']
    #     return data

class TrainEmployeeFromCSVSerializer(serializers.ModelSerializer):
	class Meta:
		model = TrainEmployeeFromCSV
		fields="__all__"
class EmployeeGroupDeviceSerializer(serializers.ModelSerializer):
      class Meta:
            model= EmployeeGroupDevice
            fields='__all__'