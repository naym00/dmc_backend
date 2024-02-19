from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ShiftManagementSerializer
from .models import ShiftAssign, ShiftManagement
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
@api_view(['GET','POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def shiftManagement(request):
	if request.method == 'GET':
		tasks = ShiftManagement.objects.all().order_by('-shift_id')
		serializer = ShiftManagementSerializer(tasks, many=True)
		return Response(serializer.data)
	if request.method == 'POST':
		print("Request Data:", request.data)
		serializer = ShiftManagementSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			print("Saved Data:", serializer.data)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		else:
			print("Errors:", serializer.errors)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET','POST','DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ShiftManagement_with_id(request,pk):
	task1 = ShiftManagement.objects.filter(shift_id=pk).first()
	print("task : ",task1)
	if task1!=None:
		task = ShiftManagement.objects.get(shift_id=pk)
		if request.method == 'GET' :
			serializer = ShiftManagementSerializer(task, many=False)
			return Response(serializer.data)

		if request.method == 'POST':
			serializer = ShiftManagementSerializer(instance=task, data=request.data,partial=True)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data)
		elif request.method == 'DELETE':
				check_shift=ShiftAssign.objects.filter(shift_id=task).first()
				if check_shift!=None:
					return Response({"message":"shift can not be deleted ,it is assigned with employee table!"},status=status.HTTP_400_BAD_REQUEST)
					
				task.delete()
				return Response({"message":"ShiftManagement successfully deleted!"})
		
	else:
		return Response({"message":"ShiftManagement id is not valid"})
	


