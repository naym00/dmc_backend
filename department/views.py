from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from devices.models import Devices
from employee.models import Employee
from .serializers import DepartmentSerializer
from .models import Department
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
@api_view(['GET','POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def department(request):
	if request.method == 'GET':
		tasks = Department.objects.all().order_by('-id')
		serializer = DepartmentSerializer(tasks, many=True)
		return Response(serializer.data)
	if request.method == 'POST':
		print("Request Data:", request.data)
		print("Request Data: department", request.data["department"])
		dept=request.data["department"]
		is_exist=Department.objects.filter(department=dept).first()
		if is_exist==None:
			serializer = DepartmentSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				print("Saved Data:", serializer.data)
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			else:
				print("Errors:", serializer.errors)
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({"message":"department already exist !!"})



@api_view(['GET','POST','DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def department_with_id(request,pk):
	task1 = Department.objects.filter(id=pk).first()

	
	print("task : ",task1)
	if task1!=None:
		task = Department.objects.get(id=pk)
		if request.method == 'GET' :
			serializer = DepartmentSerializer(task, many=False)
			return Response(serializer.data)

		if request.method == 'POST':
			serializer = DepartmentSerializer(instance=task, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data)
		elif request.method == 'DELETE':
			check_depart=Employee.objects.filter(department_id=task).first()
			if check_depart!=None:
				return Response({"message":"department can not be deleted ,it is assigned with employees table!"},status=status.HTTP_400_BAD_REQUEST)

			task.delete()
			return Response({"message":"department successfully deleted!"})
		
	else:
		return Response({"message":"department id is not valid"})
	


