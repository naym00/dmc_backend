from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from devices.check_device_status import is_device_active
from grpdev.models import GroupDevice
from .models import Devices
from .serializers import DevicesSerializer 
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

@api_view(['GET','POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def devices(request):
    if request.method == 'GET':
        dev=Devices.objects.all().order_by('-device_id')
        print("devices data :",dev)
        serializer=DevicesSerializer(dev,many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        print("Data :",request.data)
        d_ip=request.data["device_ip"]

        is_exist=Devices.objects.filter(device_ip=d_ip).first()
        if is_exist==None:
            desiSerializer=DevicesSerializer(data=request.data)
            if desiSerializer.is_valid():
                desiSerializer.save()
                return Response(desiSerializer.data,status=status.HTTP_201_CREATED)
            else:
                return Response(desiSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"device ip already exist !!"})
    
    return



@api_view(['GET','POST','DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def devices_with_id(request,pk):
    task1 = Devices.objects.filter(device_id=pk).first()
    
    if task1!=None:
        dev=Devices.objects.get(device_id=pk)
        if request.method == 'GET':
            desSerializer=DevicesSerializer(dev,many=False)
            return Response(desSerializer.data,status=status.HTTP_201_CREATED)
        if request.method == 'POST':
            desSerializer=DevicesSerializer(instance=dev,data=request.data)
            if desSerializer.is_valid():
                desSerializer.save()
                return Response(desSerializer.data,status=status.HTTP_201_CREATED)
            else:
                return Response(desSerializer.error,status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            print("devices delete :",dev)
            check_aasign=GroupDevice.objects.filter(device_id=dev).first()
            if check_aasign!=None:
                return Response({"message":"device can not be until device removed from group by device table!"},status=status.HTTP_400_BAD_REQUEST)

            dev.delete()
            return Response({"message":"devices successfully deleted!"})
    else:
        return Response({"message":"devices id is not valid"})
    return 
