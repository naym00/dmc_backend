from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from devices.check_device_status import is_device_active

from devices.models import Devices
from department.models import Department
from designation.models import Designation
from employee.models import Employee, EmployeeGroupDevice
from empgrp.models import Group
from devices.models import Devices
from employee.serializers import EmployeeGroupDeviceSerializer
from grpdev.models import GroupDevice
from shift_management.models import ShiftManagement

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def dashboard_info(request):
    data=[]
    employee=Employee.objects.all()
    total_employee=len(employee)
    device=Devices.objects.all()
    total_device=len(device)
    group=Group.objects.all()
    total_group=len(group)
    department=Department.objects.all()
    total_departments=len(department)
    active_device=Devices.objects.filter(active_status="active")
    total_active_devices=len(active_device)
    need_to_check_devices=[]
    total_chekable_devices=0
    print("devices :",active_device)
    for dev in active_device:
        print("dev :",dev)
        ip=Devices.objects.filter(device_id=dev).values_list("device_ip",flat=True)
        device_id=dev


        if is_device_active(ip[0]):
            print(dev," is active")
        else:
            total_chekable_devices+=1
            need_to_check_devices.append(str(device_id))
    shift=ShiftManagement.objects.all()
    total_shift=len(shift)
    pending=EmployeeGroupDevice.objects.all()
    serialize_data=[]
    if len(pending)>0:
        serialize=EmployeeGroupDeviceSerializer(pending,many=True)
        serialize_data= serialize.data


    data.append(
        {
            "total_employee":total_employee,
            "total_departments":total_departments,
            "total_device":total_device,
            "total_active_devices":total_active_devices,
            "total_chekable_devices":total_chekable_devices,
            "need_to_check_devices":need_to_check_devices,
            "total_group":total_group,
            "total_shift":total_shift,
            "pending_add_list":serialize_data
        }
    )
    print("dashborad data :",data)

    



    return Response({"data":data}) 