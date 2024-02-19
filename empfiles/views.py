from .serializers import EmploeeFileSerializer
from .models import EmployeeFiles
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['GET','POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def employeeFiles(request):
	if request.method == 'GET':
		tasks = EmployeeFiles.objects.all().order_by('-employee_id')
		serializer = EmploeeFileSerializer(tasks, many=True)
		return Response(serializer.data)
	if request.method == 'POST':
		print("Request Data:", request.data)
		serializer = EmploeeFileSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			print("Saved Data:", serializer.data)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		else:
			print("Errors:", serializer.errors)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET','POST','DELETE','PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def employeeFiles_with_id(request,pk):
	task = get_object_or_404(EmployeeFiles,id=pk) 
	# print("task : ",task)
	if task!=None:
		if request.method == 'GET' :
			serializer = EmploeeFileSerializer(task, many=False)
			return Response(serializer.data)

		if request.method == 'POST':
			serializer = EmploeeFileSerializer(task, data=request.data, partial=True)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		elif request.method == 'DELETE':
				task.file.delete()
				task.delete()
				return Response({"message":"EmployeeFilesFiles successfully deleted!"})
	else:
		return Response({"message":"EmployeeFilesFiles id is not valid"})


