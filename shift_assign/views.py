from helps.common.generic import Generichelps as ghelp
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from employee.models import Employee
from shift_management.models import ShiftManagement, ShiftAssign
from shift_management.serializers import ShiftAssignSerializer 
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

@api_view(['GET','POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def assign_shift(request):
    if request.method == 'GET':
        shiftAssign=ShiftAssign.objects.all().order_by('-id')

        serializer=ShiftAssignSerializer(shiftAssign,many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        print("Data :",request.data)
        shift=request.data["employee_id"]
        # is_exist=ShiftAssign.objects.filter(employee_id=shift).first()
        # if is_exist==None:
        shiftSerializer=ShiftAssignSerializer(data=request.data)
        if shiftSerializer.is_valid():
            shiftSerializer.save()
            return Response(shiftSerializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(shiftSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response({"message":"Shift already exist !!"})
    
    return



@api_view(['GET','POST','DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def assign_shift_with_id(request,pk):
    task1 = ShiftAssign.objects.filter(id=pk).first()
    if task1!=None:
        shiftAssign=ShiftAssign.objects.get(id=pk)
        if request.method == 'GET':
            shiftSerializer=ShiftAssignSerializer(ShiftAssign,many=False)
            return Response(shiftSerializer.data,status=status.HTTP_201_CREATED)
        if request.method == 'POST':
            shiftSerializer=ShiftAssignSerializer(data=request.data,partial=True)
            if shiftSerializer.is_valid():
                shiftSerializer.save()
                return Response(shiftSerializer.data,status=status.HTTP_201_CREATED)
            else:
                return Response(shiftSerializer.error,status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            print("delete ShiftAssign :",shiftAssign)
            shiftAssign.delete()
            return Response({"message":"Shift successfully deleted!"})
    else:
        return Response({"message":"Shift is not valid"})

    return 

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def assign_shift_bulk(request, shiftid):
    if ShiftManagement.objects.filter(shift_id=shiftid).exists():
        employee_id_list = request.data.get('employee_id_list', [])
        culdnotaddshift=[]
        preparedata = []
        for employee_id in employee_id_list:
            if Employee.objects.filter(employee_id=employee_id).exists():
                preparedata.append({'employee_id': employee_id, 'shift_id': shiftid})
            else:
                culdnotaddshift.append(employee_id)
        if preparedata:
            shiftassignserializer=ShiftAssignSerializer(data=preparedata, many=True)
            if shiftassignserializer.is_valid(raise_exception=True):
                shiftassignserializer.save()
        return Response({"message": {
            "error": "",
            "success_empid": [item['employee_id'] for item in preparedata],
            "failed_empid": culdnotaddshift
        }})
    else: return Response({"message": {
            "error": "shift id is not valid!",
            "success_empid": [],
            "failed_empid": []
        }})