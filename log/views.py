from helps.common.generic import Generichelps as ghelp
from datetime import datetime, timedelta
from django.utils import timezone

import json
from urllib.request import HTTPDigestAuthHandler
import pytz
from requests.auth import HTTPDigestAuth
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import requests
from attendance_report.models import AttendanceReport
from attendance_report.views import attendance_create, insert_attendance_log
from department.models import Department
from designation.models import Designation
from employee.serializers import EmployeeGroupDeviceSerializer
from employee.views import delete_info, train_employee_with_image
from syncInfo.views import syncInfo

from employee.models import Employee, EmployeeGroupDevice
from .serializers import LogSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import re
from .models import Log
from devices.models import Devices
from devices.serializers import DevicesSerializer
import ipaddress
from structuedlog.views import insert_structed_log
from login.models import LogInLog
from syncInfo.models import SyncInfoTable
from syncInfo.serializers import SyncInfoTableSerializer 
from devices.check_device_status import is_device_active
from rest_framework.pagination import PageNumberPagination
from grpdev.models import GroupDevice
from empgrp.models import Group
from django.db.models import Min, Max


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def raw_log(request):
    date_filter = request.GET.get('date', None)
    employee_id_filter = request.GET.get('employee_id', None)
    group_filter=request.GET.get('group_id', None)
    department_filter=request.GET.get('department_id', None)
    designation_filter=request.GET.get('designation_id', None)

    valid_column_accessor = ['r_clsf_record_id', 'device_id', 'CardName', 'InTime', 'RecNo', 'RoomNumber', 'Status', 'Type', 'employee_id', 'department', 'designation', 'department_name', 'designation_name', 'logdate']
    tasks = Log.objects.all()
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
    else: tasks = tasks.order_by('-r_clsf_record_id')

    # dept_exist=Department.objects.filter(id=department_filter).first()
    # desi_exist=Designation.objects.filter(id=designation_filter).first()
    # grp_exist=GroupDevice.objects.filter(group_id=group_filter).first()
    # emp_exist=Employee.objects.filter(employee_id=employee_id_filter).first()

    # if dept_exist==None or desi_exist==None or grp_exist==None or emp_exist==None:
    #     return Response({"message":"Data not found","results": []})
    if date_filter:
        tasks=tasks.filter(InTime__startswith=date_filter)
    if department_filter:
        print("department_filter :",department_filter)
        
        tasks=tasks.filter(department__in=department_filter)
        
    if designation_filter:
        print("designation_filter :",designation_filter)
        tasks=tasks.filter(designation__in=designation_filter)
    if group_filter:
        grp=Group.objects.get(group_id=group_filter)
        devices_by_group=GroupDevice.objects.filter(group_id=group_filter).values_list('device_id', flat=True)
        print(devices_by_group)
        tasks=tasks.filter(device_id__in=devices_by_group)
    if employee_id_filter:
        tasks=tasks.filter(employee_id=employee_id_filter)

    paginator = PageNumberPagination()
    # paginator.page_size = 10  # Set the number of items per page
    paginator.page_size = int(request.GET.get('page_size', 10))

    result_page = paginator.paginate_queryset(tasks, request)

    serializer = LogSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def log_with_minutes(request,pk):
    logintoken=request.headers['Authorization']
    logintoken=logintoken.replace("Bearer ","")
    employee_id_found=LogInLog.objects.filter(token=str(logintoken)).values_list("employee_id",flat=True)
    print("login token :",logintoken)
    print("loged in employee :",employee_id_found[0])
    last_sync_time=SyncInfoTable.objects.all().order_by("-id")[:1]
    last_sync_time_serializer=SyncInfoTableSerializer(last_sync_time,many=True)
    dt=datetime.now()
    if len(last_sync_time_serializer.data)>0:

        print("last sync info :",last_sync_time_serializer.data[0]['syncTime'])
        dt=last_sync_time_serializer.data[0]['syncTime']

        
    stime = datetime.now() - timedelta(minutes=pk)
    # stime = datetime.strptime(stime, "%Y-%m-%d %H:%M:%S")

    # Specify the original time zone (assuming it's Dhaka)
    original_timezone = pytz.timezone('Asia/Dhaka')

    # Localize the datetime object to the original time zone
    stime = original_timezone.localize(stime)

    # Convert to UTC
    stime_utc = stime.astimezone(pytz.utc)

    # Convert datetime to timestamp
    tstamp = stime_utc.timestamp()
    print("last sync time :",tstamp)

    
    start=int(tstamp)
    current_dt=datetime.now(original_timezone)

    end=current_dt.timestamp()
    # device=Device.objects.none()
    print("In get start :",start,"end :",end)

    device_id=Devices.objects.all().values_list("device_id","active_status",flat=False)
    print("device ip:",device_id[0])
    log=[]

    print("device_id :",id," start : ",start,"end : ",end)
    for did in device_id:
        print("ip :",did[0])
        if did[1]=="active" :
            print("started syncking ...")

            logs=get_data_by_ip(str(did[0]),start,end)
            log.append(logs)

    loged_employee=Employee.objects.get(employee_id=employee_id_found[0])
    timezone = pytz.timezone('Asia/Dhaka')
    current_datetime = datetime.now(timezone)
    gmt6_datetime = current_datetime.astimezone(timezone)
    print(current_datetime)

    syncInfo(current_datetime,loged_employee)

    return Response({"Sync Status":log})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def log(request):
    if request.method=="POST":
         
        logintoken=request.headers['Authorization']
        logintoken=logintoken.replace("Bearer ","")
        employee_id_found=LogInLog.objects.filter(token=str(logintoken)).values_list("employee_id",flat=True)
        print("login token :",logintoken)
        print("loged in employee :",employee_id_found[0])
        last_sync_time=SyncInfoTable.objects.all().order_by("-id")[:1]
        last_sync_time_serializer=SyncInfoTableSerializer(last_sync_time,many=True)
        dt=datetime.now()
        if len(last_sync_time_serializer.data)>0:

            print("last sync info :",last_sync_time_serializer.data[0]['syncTime'])
            dt=last_sync_time_serializer.data[0]['syncTime']
        
            

        # print("last sync info :",last_sync_time_serializer.data[0]['syncTime'])
        # dt=last_sync_time_serializer.data[0]['syncTime']
        stime = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S") - timedelta(hours=6)
        # stime = datetime.strptime(stime, "%Y-%m-%d %H:%M:%S")

        # Specify the original time zone (assuming it's Dhaka)
        original_timezone = pytz.timezone('Asia/Dhaka')

        # Localize the datetime object to the original time zone
        stime = original_timezone.localize(stime)

        # Convert to UTC
        stime_utc = stime.astimezone(pytz.utc)

        # Convert datetime to timestamp
        tstamp = stime_utc.timestamp()
        print("last sync time :",tstamp)

        
        start=int(tstamp)
        current_dt=datetime.now(original_timezone)

        end=current_dt.timestamp()
        # device=Device.objects.none()
        print("start :",start,"end :",end)


        ###ip based seraching

        # DeviceLocalIP=Device.objects.all().values_list("device_ip","active_status",flat=False)
        # print("device ip:",DeviceLocalIP[0])
        # log=[]
        # if 'ip' in request.data:

        #     ip = request.data["ip"]
        #     print("ip :",ip," start : ",start,"end : ",end)
        #     for dip in DeviceLocalIP:
        #           if dip[0]==ip and dip[1]=="active":

        #             logs=get_data_by_ip(str(dip[0]),start,end)
        #             log.append({ip:logs})
        # else:
        #      for ip in DeviceLocalIP:
        #           if ip[1]=="active":
        #             logs=get_data_by_ip(ip[0],start,end)
        #             log.append({ip[0]:logs})
        # print("log :",log)
        # return Response({"log":log})
    ###id based searching
        device_id=Devices.objects.all().values_list("device_id","active_status",flat=False)
        print("device ip:",device_id[0])
        log=[]
        if 'device_id' in request.data:

            id = request.data["device_id"]
            for i in id:
                print("device id :",i)

            print("device_id :",id," start : ",start,"end : ",end)
            for did in device_id:
                if did[0] in id and did[1]=="active" :
                    print("started syncking ...")

                    logs=get_data_by_ip(str(did[0]),start,end)
                    log.append(logs)
                elif did[0] in id:
                    log.append({did[0]:False})

                    
                
        else:
             for id in device_id:
                if id[1]=="active":
                    logs=get_data_by_ip(id[0],start,end)
                    log.append(logs)
                else:
                    log.append({id[0]:False})
        # print("log :",log)
        loged_employee=Employee.objects.get(employee_id=employee_id_found[0])
        timezone = pytz.timezone('Asia/Dhaka')
        current_datetime = datetime.now(timezone)
        gmt6_datetime = current_datetime.astimezone(timezone)
        print(current_datetime)

        syncInfo(current_datetime,loged_employee)

        return Response({"Sync Status":log})









def get_data_by_ip(did,start,end):
            print("inside the get log function")
            # ip=Devices.objects.filter(device_id=did).values_list("device_ip",flat=True)

            deviceip, deviceusername, devicepassword, deviceactivity = ghelp().getDeviceIpUsernamePassword(Devices, did)

            datas=[]
            dev_info={}
            if is_device_active(deviceip):
                dev_info={did:True}
            
                url=f"http://{deviceip}/cgi-bin/recordFinder.cgi?action=find&name=AccessControlCardRec&StartTime={int(start)}&EndTime={int(end)}&count=1000"
                response=requests.get(url,auth=HTTPDigestAuth(deviceusername, devicepassword))
                print("response url :",response.url)
                data=response.text.split('\n')
                # print("data :",data)
                records = []

                # Split the text into lines
                lines = data

                # Remove empty lines
                lines = [line for line in lines if line.strip()]

                current_index = None
                current_record = {}

                for line in lines:
                    # Extract the index, field, and value using regular expressions
                    match = re.match(r'records\[(\d+)\]\.(.*?)=(.*)', line)
                    if match:
                        index = int(match.group(1))
                        field_name = match.group(2)
                        value = match.group(3)

                        if index != current_index:
                            if current_record:
                                records.append(current_record)
                            current_index = index
                            current_record = {}

                        current_record[field_name] = value

                if current_record:
                    records.append(current_record)
                # print("records :",records)
                

                total_length=len(records)
                total_log_table=Log.objects.all()
                if len(total_log_table)>0:
                    Log.objects.all().update(last_synced=False)

                for index in range(len(records)):
                    print("index :",index)
                    CardName=records[total_length-index-1]['CardName']
                    InTime=records[total_length-index-1]['CreateTime']
                    RecNo=records[total_length-index-1]['RecNo']
                    RoomNumber=records[total_length-index-1]['RoomNumber']
                    Status=records[total_length-index-1]['Status']
                    Type=records[total_length-index-1]['Type']
                    image_url=records[total_length-index-1]['URL']
                    employee_id = records[total_length-index-1]['UserID']
                    devi=Devices.objects.get(device_id=did)
                    # employee=Employee.objects.get(employee_id=employee_id)
                    # intime=datetime.utcfromtimestamp(int(InTime.rstrip('\r')))
                    utc_datetime = datetime.utcfromtimestamp(int(InTime.rstrip('\r')))


                    # Specify the UTC timezone
                    utc_timezone = pytz.timezone('UTC')
                    utc_datetime = utc_timezone.localize(utc_datetime)

                    # Convert to the desired timezone (GMT+6)
                    gmt6_timezone = pytz.timezone('Asia/Dhaka')  # Replace with the appropriate timezone identifier
                    gmt6_datetime = utc_datetime.astimezone(gmt6_timezone)-timedelta(hours=6)

                    
                    if employee_id !='\r':
                        exist=employee=Employee.objects.filter(employee_id=str(employee_id.rstrip('\r'))).first()
                        if exist!=None:
                            print("employee_id :",str(employee_id.rstrip('\r')))
                            employee=Employee.objects.get(employee_id=str(employee_id.rstrip('\r')))
                            employee_desig_depart=Employee.objects.filter(employee_id=str(employee_id.rstrip('\r'))).values_list("department","designation",flat=False)
                            print("employee_desig_depart : ",employee_desig_depart)
                            print("dersignation :",employee_desig_depart[0][1],",department :",employee_desig_depart[0][0])
                            department_ins=Department.objects.get(id=employee_desig_depart[0][0])
                            designation_ins=Designation.objects.get(id=employee_desig_depart[0][1])


                            # device_id=Device.objects.filter(device_ip=ip).values_list("device_id",flat=True)
                            info={
                                "device_id":did,
                                "CardName":CardName.rstrip('\r'),
                                "InTime":gmt6_datetime,
                                "RecNo":int(RecNo.rstrip('\r')),
                                "RoomNumber":RoomNumber.rstrip('\r'),
                                "Status":int(Status.rstrip('\r')),
                                "Type":Type.rstrip('\r'),
                                "image_url":image_url.rstrip('\r'),
                                "employee_id":employee_id.rstrip('\r')

                                }
                            check_record_number=Log.objects.filter(RecNo=int(RecNo.rstrip('\r'))).values_list("RecNo",flat=False)
                            print("record number :",check_record_number.count())
                            if check_record_number.count()==0:
                                # gmt6_timezone = pytz.timezone("GMT+6")
                                # in_time_gmt6 = datetime(2023, 11, 26, 11, 41, 20, tzinfo=gmt6_timezone)
                                print("log InTime :",gmt6_datetime.replace(tzinfo=timezone.utc))
                                InTime=gmt6_datetime.replace(tzinfo=timezone.utc),
                                print("InTime: ",InTime[0].replace(tzinfo=None))
                                in_t=InTime[0].replace(tzinfo=None)

                                ins=Log(
                                    device_id=devi,
                                    CardName=CardName.rstrip('\r'),
                                    InTime=gmt6_datetime.replace(tzinfo=timezone.utc),
                                    RecNo=int(RecNo.rstrip('\r')),
                                    RoomNumber=RoomNumber.rstrip('\r'),
                                    Status=int(Status.rstrip('\r')),
                                    Type=Type.rstrip('\r'),
                                    image_url=image_url.rstrip('\r'),
                                    employee_id=employee,
                                    department=department_ins,
                                    designation=designation_ins,
                                    last_synced=True,
                                    logdate=in_t.date()

                                    )
                                
                                ins.save()
                                print("saved")
                                insert_structed_log(device_id=devi,employee_id=employee,username=CardName.rstrip('\r'),InTime=gmt6_datetime.replace(tzinfo=timezone.utc),designation=designation_ins,department=department_ins)
                                # insert_attendance_log(device_id=devi,employee_id=employee,username=CardName.rstrip('\r'),InTime=gmt6_datetime.replace(tzinfo=timezone.utc),designation=designation_ins,department=department_ins,count=100)
            
                            else:
                                # insert_attendance_log(device_id=devi,employee_id=employee,username=CardName,InTime=gmt6_datetime.replace(tzinfo=timezone.utc))

                                # insert_structed_log(device_id=devi,employee_id=employee,username=CardName,InTime=gmt6_datetime.replace(tzinfo=timezone.utc))

                                print("data already synced")
                            datas.append(info)
                print("length : ",len(records))
                check_records=Log.objects.all().order_by("r_clsf_record_id")
                serialize=LogSerializer(check_records,many=True)
                
                serialize=LogSerializer(check_records,many=True)

                total=(total_length-1)
                st=datetime.utcfromtimestamp(start).date()
                ed=datetime.utcfromtimestamp(end).date()
                current_date = st
                while current_date <= ed:
                    # Perform operations with 'current_date'
                    print(current_date)  # Example: Print the current date

                    # Assuming log_date is the specific date for which you want to find check-in and check-out times

                     # Query to find first check-in time for each employee on the specific logdate
                    first_check_ins = Log.objects.filter(logdate=current_date).values('employee_id').annotate(first_check_in=Min('InTime'))

                    # Query to find last check-out time for each employee on the specific logdate
                    last_check_outs = Log.objects.filter(logdate=current_date).values('employee_id').annotate(last_check_out=Max('InTime'))
                    device_id=Log.objects.filter(logdate=current_date).values_list("device_id").first()

                    # Iterate through results to print first check-in and last check-out times for each employee
                    for employee_check_in in first_check_ins:
                        employee_id = employee_check_in['employee_id']
                        first_check_in_time = employee_check_in['first_check_in']
                        
                        # Fetch the last check-out time for the same employee on the specific logdate
                        last_check_out_time = next((check_out['last_check_out'] for check_out in last_check_outs if check_out['employee_id'] == employee_id), None)
                        
                        print(f"Employee ID: {employee_id}, First check-in time: {first_check_in_time}, Last check-out time: {last_check_out_time}")
                        
                        # device_id =
                        # group_id=
                        # employee_id=
                        # username =
                        # InTime=
                        # OutTime=
                        # delay_minutes = 
                        # total_work_minutes=
                        # cumalative_work_minutes=
                        # department=
                        # designation=
                        # department_name = 
                        # designation_name =
                        # date=
                        employee_ins=Employee.objects.get(employee_id=employee_id)
                        print("device_id :",device_id)
                        device_ins=Devices.objects.get(device_id=device_id[0])
                        group_desig_depart_ins=Employee.objects.filter(employee_id=employee_id).values_list("group_id","designation","department",flat=False)
                        group_id=Group.objects.get(group_id=group_desig_depart_ins[0][0])
                        designation=Designation.objects.get(id=group_desig_depart_ins[0][1])
                        department=Department.objects.get(id=group_desig_depart_ins[0][2])
                        designation_name=Designation.objects.filter(id=group_desig_depart_ins[0][1]).values_list("designation",flat=True)
                        department_name=Department.objects.filter(id=group_desig_depart_ins[0][2]).values_list("department",flat=True)

                        username=Employee.objects.filter(employee_id=employee_id).values_list("username",flat=True)



                        
                        attendance=AttendanceReport(
                        device_id =device_ins,
                        group_id=group_id,
                        employee_id=employee_ins,
                        username =username,
                        InTime=first_check_in_time,
                        OutTime=last_check_out_time,
                        delay_minutes = 0,
                        total_work_minutes=0,
                        cumalative_work_minutes=0,
                        department=department,
                        designation=designation,
                        department_name =department_name,
                        designation_name = designation_name,
                        date=current_date

                        )
                        attendance.save()
                        # device_id = models.ForeignKey("devices.Devices",on_delete=models.CASCADE)
                        # CardName = models.CharField(max_length=100,default="-",null=True)
                        # InTime=models.DateTimeField(null=True)
                        # RecNo=models.IntegerField(default=0,null=True)
                        # RoomNumber=models.CharField(default="-",null=True,max_length=100)
                        # Status=models.IntegerField(default=0,null=True)
                        # Type=models.CharField(default="-",null=True,max_length=100)
                        # image_url=models.CharField(max_length=100,default="-",null=True)
                        # employee_id=models.ForeignKey("employee.Employee",on_delete=models.CASCADE,null=True)
                        # department=models.ForeignKey("department.Department",on_delete=models.CASCADE,null=True)
                        # designation=models.ForeignKey("designation.Designation",on_delete=models.CASCADE,null=True)
                        # department_name = models.CharField(max_length=100, null=True, blank=True)
                        # designation_name = models.CharField(max_length=100, null=True, blank=True)
                        # last_synced=models.BooleanField(null=True,default=False)
                        # logdate = models.DateField(null=True, default=timezone.now)

                    # Increment the current_date by one day for the next iteration
                    current_date += timedelta(days=1)


                # insert_attendance_log(count=total)
                # attendance_create(total)






                # for i in range(len(records)):
                #     print("")
                    

            else:
                dev_info={did:False}
            



            return dev_info

def auto_save():
    device=Devices.objects.all().order_by('-device_id')
    serializer=DevicesSerializer(device,many=True)
    for d in serializer.data:
        if d["active_status"]=="active" and is_device_active(d["device_ip"]):
            timezone = pytz.timezone('Asia/Dhaka')  # Replace 'Asia/Dhaka' with the desired timezone

            # Get the current time in the specified timezone
            current_time = datetime.now(timezone)

            # Calculate the start time by subtracting 5 minutes
            start_time = current_time - timedelta(minutes=180)
            
            start=int(start_time.timestamp())
            end=int(current_time.timestamp())

            print("device id :",d["device_id"])
            get_data_by_ip(d["device_id"],start,end)
            # check_emp_group_device()
            
##check EmployeeGroupDevice is there is any entry
def check_emp_group_device():
    datas=EmployeeGroupDevice.objects.all()
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
                if is_device_active(device_ip[0]) and data["action"] =="add":
                    employee_info=Employee.objects.get(employee_id=data["employee_id"])

                    train_employee_with_image(employee_info)
                    del_row=EmployeeGroupDevice.objects.filter(employee_id=data["employee_id"])
                    del_row.delete()
                if  is_device_active(device_ip[0]) and data["action"]=="delete":
                    emp_id=Employee.objects.filter(employee_id=data["employee_id"]).values_list("employee_id",flat=True)
                    delete_info(emp_id[0])
                    del_row=EmployeeGroupDevice.objects.filter(employee_id=data["employee_id"])
                    del_row.delete()

                if is_device_active(device_ip[0]) and differ.days> 10:
                    del_row=EmployeeGroupDevice.objects.filter(employee_id=data["employee_id"])
                    del_row.delete()










    #check  "action" colummn,
    #if "action"=="add":
    
    #ping the device_id ,if the device is active ,then do as per action column  into the device
    ##if the device not active or not able to ping and job_start_date > 10 days then,delete the job
    # data.delete()
    ###check if there is any entry in the database.If there is any entry,then get their info
    

