from django.shortcuts import render
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from employee.models import Employee
from login.models import LogInLog
from syncInfo.models import SyncInfoTable
from archive_log.models import Archivelog
from django.db.models import Max


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def security_info(request,pk):
    data=[]
    employee_ins=Employee.objects.filter(employee_id=pk)
    login=LogInLog.objects.filter(employee_id=employee_ins[0]).aggregate(Max('login_date'))['login_date__max']
    print("login :",login)
    sync=SyncInfoTable.objects.filter(employee_id=employee_ins[0]).aggregate(Max('syncTime'))['syncTime__max']
    print("sync :",sync)
    archive=Archivelog.objects.filter(employee_id=employee_ins[0]).aggregate(Max('archive_time'))['archive_time__max']
    print("archive :",archive)
    data.append(
        {
            "last_login":login,
            "last_sync":sync,
            "last_log_archive_time":archive
        }
    )


    return Response({"message":"successfull","data":data})