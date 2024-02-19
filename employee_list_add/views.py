from datetime import datetime
from django.shortcuts import render
from devices.check_device_status import is_device_active
from devices.models import Devices
from rest_framework.decorators import api_view
from employee.models import Employee, EmployeeGroupDevice
from employee.serializers import EmployeeGroupDeviceSerializer, EmployeeSerializer
from employee.views import delete_info, train_employee_with_image

from rest_framework.response import Response


# Create your views here.

@api_view(['GET'])
def check_emp_group_device(request):
    datas=EmployeeGroupDevice.objects.all()
    total_serializer=EmployeeGroupDeviceSerializer(datas,many=True)
    print("datas :")
    print(len(datas))
    
    if len(datas)>0:
        for i in range(len(datas)):
            print("data :")
            print(datas[i])

            
            if datas[i]:
                serializer=EmployeeGroupDeviceSerializer(datas[i],many=False)
                data=serializer.data
                print("data :",data)
                print("job start date :",data["job_start_date"])
                datetime_obj = datetime.strptime(data["job_start_date"], "%Y-%m-%dT%H:%M:%S.%f%z")
                differ=datetime.now(datetime_obj.tzinfo)-datetime_obj
                device_ip=Devices.objects.filter(device_id=data["device_id"]).values_list("device_ip",flat=True)
                print("ip : ",device_ip[0]," , action : ",data["action"])
                print("employee_id :",serializer.data["employee_id"])
                device_id=Devices.objects.get(device_id=data["device_id"])


                if is_device_active(device_ip[0]) and data["action"] =="add":
                    employee_info=Employee.objects.get(employee_id=data["employee_id"])
                    info_serializer=EmployeeSerializer(employee_info)
                    print("inside add :",info_serializer.data)
                    all_info=info_serializer.data

                    train_employee_with_image(all_info)

                    del_row=EmployeeGroupDevice.objects.filter(device_id=device_id)
                    del_row.delete()
                if  is_device_active(device_ip[0]) and data["action"]=="delete":
                    emp_id=Employee.objects.filter(employee_id=data["employee_id"]).values_list("employee_id",flat=True)
                    delete_info(emp_id[0])
                    del_row=EmployeeGroupDevice.objects.filter(device_id=device_id)
                    del_row.delete()

                if is_device_active(device_ip[0]) and differ.days> 10:
                    del_row=EmployeeGroupDevice.objects.filter(device_id=device_id)
                    del_row.delete()
    return Response({"message":"trained updated employee","data":total_serializer.data})
