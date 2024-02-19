from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from employee.models import Employee
from .models import Designation
from .serializers import DesignationSerializer 
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

@api_view(['GET','POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def designation(request):
    if request.method == 'GET':
        designation=Designation.objects.all().order_by('-id')

        serializer=DesignationSerializer(designation,many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        print("Data :",request.data)
        desig=request.data["designation"]
        is_exist=Designation.objects.filter(designation=desig).first()
        if is_exist==None:
            desiSerializer=DesignationSerializer(data=request.data)
            if desiSerializer.is_valid():
                desiSerializer.save()
                return Response(desiSerializer.data,status=status.HTTP_201_CREATED)
            else:
                return Response(desiSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"designation already exist !!"})
    
    return



@api_view(['GET','POST','DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def designation_with_id(request,pk):
    task1 = Designation.objects.filter(id=pk).first()
    if task1!=None:
        designation=Designation.objects.get(id=pk)
        if request.method == 'GET':
            desSerializer=DesignationSerializer(designation,many=False)
            return Response(desSerializer.data,status=status.HTTP_201_CREATED)
        if request.method == 'POST':
            desSerializer=DesignationSerializer(instance=designation,data=request.data)
            if desSerializer.is_valid():
                desSerializer.save()
                return Response(desSerializer.data,status=status.HTTP_201_CREATED)
            else:
                return Response(desSerializer.error,status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            print("delete designation :",designation)
            check_desi=Employee.objects.filter(designation_id=designation).first()
            if check_desi!=None:
                return Response({"message":"designation can not be deleted ,it is assigned with employees table!"},status=status.HTTP_400_BAD_REQUEST)

            designation.delete()
            return Response({"message":"designation successfully deleted!"})
    else:
        return Response({"message":"designation id is not valid"})

    return 


