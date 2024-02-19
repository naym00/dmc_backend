from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication
from devices.check_device_status import is_device_active
from devices.models import Devices
from devices.serializers import DevicesSerializer
# Create your views here.

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def devices_status(request):
        dev=Devices.objects.all().order_by('-device_id')
        print("devices data :",dev)
        devserializer=DevicesSerializer(dev,many=True)
        dev_datas=devserializer.data
        dev_status=[]
        print("count : ",len(dev_datas))
        for i in range(len(dev_datas)):
            if dev_datas[0]["device_ip"]==None:
                dev_status.append({"device_id":dev_datas[i]["device_id"],"device_ip":"null","active_status":dev_datas[i]["active_status"],"present_active_status": "inactive"})
                continue
            print(dev_datas[0]["device_id"])
            present_active_status= is_device_active(dev_datas[i]["device_ip"])
            present_active_status_str=""
            if present_active_status==True:
                present_active_status_str="active"
            else:
                present_active_status_str="inactive"
            
            dev_status.append({"device_id":dev_datas[i]["device_id"],"device_ip":dev_datas[i]["device_ip"],"active_status":dev_datas[i]["active_status"],"present_active_status": present_active_status_str})
        print("device_status",dev_status)
        return Response({"message":dev_status})


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def devices_status_with_id(request,pk):
    task1 = Devices.objects.filter(device_id=pk).first()
    
    if task1!=None:
        dev=Devices.objects.get(device_id=pk)
        devserializer=DevicesSerializer(dev,many=False)
        dev_datas=devserializer.data
        dev_status=[]

        print("count : ",len(dev_datas))

        print(dev_datas["device_id"])
        present_active_status= is_device_active(dev_datas["device_ip"])
        present_active_status_str=""
        if present_active_status==True:
            present_active_status_str="active"
        else:
            present_active_status_str="inactive"
        if dev_datas["device_ip"]==None:
            present_active_status_str="inactive"
        
            
            dev_status.append({"device_id":dev_datas["device_id"],"device_ip":dev_datas["device_ip"],"active_status":dev_datas["active_status"],"present_active_status": present_active_status_str})
        print("device_status",dev_status)
        return Response({"message":dev_status})

    
    return

