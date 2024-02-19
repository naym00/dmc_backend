from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render
import pytz
from department.models import Department
from designation.models import Designation
from grpdev.models import GroupDevice
from structuedlog.models import StructuredLog
from structuedlog.serializers import StructuredLogSerializer
from empgrp.models import Group
from employee.models import Employee
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.pagination import PageNumberPagination
# Create your views here.


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def structured_log(request):
    date_filter = request.GET.get('date', None)
    employee_id_filter = request.GET.get('employee_id', None)
    group_filter=request.GET.get('group_id', None)
    department_filter=request.GET.get('department_id', None)
    designation_filter=request.GET.get('designation_id', None)

    valid_column_accessor = ['ID', 'device_id', 'group_id', 'employee_id', 'username', 'InTime', 'department', 'designation', 'department_name', 'designation_name']
    tasks = StructuredLog.objects.all()
    column_accessor = request.GET.get('column_accessor')
    direction = request.GET.get('direction')
    if column_accessor:
        if column_accessor in valid_column_accessor:
            if direction:
                if isinstance(direction, str):
                    if direction in ['ASCENDING', 'Ascending', 'ascending', 'ASC', 'asc', 'Asc']:
                        try: tasks = tasks.order_by(column_accessor)
                        except: pass
                    elif direction in ['DESCENDING', 'Descending', 'descending', 'DESC', 'desc', 'Desc']:
                        try: tasks = tasks.order_by(f'-{column_accessor}')
                        except: pass
            else:
                try: tasks = tasks.order_by(column_accessor)
                except: pass
    else: tasks = tasks.order_by('-ID')

    # if dept_exist==None or desi_exist==None or grp_exist==None or emp_exist==None:
    #         return Response({"message":"Data not found","results": []})
    if department_filter:
            print("department_filter :",department_filter)
            
            
            # dept=Department.objects.get(id=department_filter)
            # print("dept :",dept)
            tasks=tasks.filter(department__in=department_filter)
            
    if designation_filter:
            print("designation_filter :",designation_filter)

            # desi=Designation.objects.get(id=designation_filter)
            # print("desi :",desi)
            tasks=tasks.filter(designation__in=designation_filter)
    if group_filter:
        tasks=tasks.filter(group_id=group_filter)
    if employee_id_filter:
        tasks=tasks.filter(employee_id=employee_id_filter)
    if date_filter:
        tasks=tasks.filter(InTime__startswith=date_filter)
    paginator = PageNumberPagination()
    # paginator.page_size = 10  # Set the number of items per page
    paginator.page_size = int(request.GET.get('page_size', 10))

    result_page = paginator.paginate_queryset(tasks, request)

    serializer = StructuredLogSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)


def insert_structed_log(device_id,employee_id,username,InTime,designation,department):
    print("device_id :",device_id,"employee_id :",employee_id,"username :",username,"InTime :",InTime)
    group=GroupDevice.objects.filter(device_id=device_id).values_list("group_id",flat=True)
    group_id=Employee.objects.filter(employee_id=employee_id).values_list("group_id")
    # emp=Employee.objects.get(employee_id=employee_id)
    print("employee touple:",group_id[0])
    print("employee:",group_id[0][0])

    print("total group :",len(group_id))
    for i in range(len(group_id)):
        grp=Group.objects.get(group_id=group_id[0][i])
        print("staging log")
        print("structured intime :",InTime)
        # utc_datetime = datetime.utcfromtimestamp(int(InTime.rstrip('\r')))

        # utc_datetime = datetime.utcfromtimestamp(int(InTime.rstrip('\r')))


        # # Specify the UTC timezone
        # utc_timezone = pytz.timezone('UTC')
        # utc_datetime = utc_timezone.localize(utc_datetime)

        # # Convert to the desired timezone (GMT+6)
        # gmt6_timezone = pytz.timezone('Asia/Dhaka')  # Replace with the appropriate timezone identifier
        # gmt6_datetime = utc_datetime.astimezone(gmt6_timezone)
        # print("log time 2 :",gmt6_datetime)

        data = StructuredLog(
            device_id=device_id,
            group_id=grp,
            employee_id=employee_id,
            username=username,
            InTime=InTime,
            designation=designation,
            department=department
        )
        data.save()

    return
