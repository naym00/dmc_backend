from helps.common.generic import Generichelps as ghelp
import base64
from datetime import datetime, timedelta
import os

import requests
from devices.check_device_status import is_device_active
from devices.models import Devices
from dmc import settings
from pathlib import Path
from dmc.settings import MEDIA_DIR,BASE_DIR
from django.http import FileResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import GroupDevice
from .serializers import GroupDeviceSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from employee.models import Employee, resize_image
from employee.serializers import EmployeeSerializer
from empgrp.models import Group
from empgrp.serializers import GroupSerializer
from requests.auth import HTTPDigestAuth
# Create your views here.
@api_view(['GET','POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def empgrpdev(request):
    grpdev = GroupDevice.objects.all().order_by('-id')
    if request.method =='GET':
        serializer=GroupDeviceSerializer(grpdev,many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        is_exist=GroupDevice.objects.filter(group_id=request.data['group_id'], device_id=request.data["device_id"]).first()
        # print("is_exist :",is_exist)
        if is_exist==None:
          serializer=GroupDeviceSerializer(data=request.data)
        
          if serializer.is_valid():
              serializer.save()
              print(serializer.data)
              # employee_list=Employee.objects.filter()
              group_ins=Group.objects.filter(group_id=serializer.data["group_id"])
              print("group_ins :",group_ins)
              group_check=GroupDevice.objects.filter(group_id=group_ins[0]).first()
              if group_check !=None:
                # device_list=GroupDevice.objects.filter(group_id=group_ins[0]).values_list("group_id","device_id",flat=False)
                # print("device list :",device_list)
                employee_list=Employee.objects.filter(group_id=group_ins[0])
                for i in range(len(employee_list)):
                    employee_info=Employee.objects.get(employee_id=employee_list[i])
                    info_serializer=EmployeeSerializer(employee_info,many=False)
                    if info_serializer.data["image"] is not None:
                        img_path = str(BASE_DIR)+info_serializer.data["image"]
                        print("employee_id :",info_serializer.data["employee_id"]," employee_name :",info_serializer.data["username"],"image :",info_serializer.data["image"])
                        info_data=info_serializer.data
                        

                        if img_path is None or not os.path.exists(img_path):
                        
                            print(info_serializer.data["image"],"path not found :")
                        else:
                              train_employee_on_new_device(info_data,serializer.data["device_id"])
                            
                            # with open(img_path, "rb") as image_file:
                            #     image_binary = image_file.read()
                            #     # Encode the binary data as base64
                            #     image_base64 = base64.b64encode(image_binary).decode('utf-8')
                            #     train_employee_on_new_device(info_data,serializer.data["device_id"])
                            #     print("employee id :",info_serializer.data["employee_id"],"image :",image_base64)


                #     print("employee info :",info_serializer)
                # print("employee_list :",employee_list)


              return Response(serializer.data)
          else:
              return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
             return Response({"message":"device already assigned!!!"})

@api_view(['GET','POST','DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def empgrpdev_with_id(request,pk):
    find = GroupDevice.objects.filter(id=pk).first()

    if find!=None:
        grpdev = GroupDevice.objects.get(id=pk)

        if request.method == 'GET':
            gserializer =GroupDeviceSerializer(grpdev)
            return Response(gserializer.data)
        if  request.method == 'POST':
            pserializer= GroupDeviceSerializer(instance=grpdev,data=request.data)
            if pserializer.is_valid():
                pserializer.save()
                return Response(pserializer.data)
            else:
                return Response(pserializer.errors,status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            grpdev.delete()
            return Response({"message":"Deletion successful!!"})
    else:
        return Response({"message":"Employee id is not valid"})
    


def train_employee_on_new_device(data,id):
	print("E_ID :",data['employee_id'])
	print("Name :",data["username"])
	print("Surname",data["username"].replace(" ","_"))
	# image_path = os.path.join(settings.MEDIA_ROOT, str(employee.employee_id),
	#  "image.jpg")
	img=data["image"].replace("/media","")
	# img=img.replace("/","\\")
	# image_path = os.path.join(settings.MEDIA_ROOT,data['employee_id'],data["username"]+".jpg")
	img = img.lstrip('/')
	image_path = Path(settings.MEDIA_ROOT) / img
	print("img :",img)
	print("media root :",settings.MEDIA_ROOT)
	print("image path :",image_path)
	print("inside train :",data)
	print("register date : ",data['registration_date'])
	print("validity_date :",data["validity_date"])
    
	reg_date=datetime.now()
	reg_date=reg_date.strftime("%Y%m%d")
	valid_date=datetime.now()+timedelta(days=5*365)
	valid_date=valid_date.strftime("%Y%m%d")
	cardno=int(data["cardNo"])
	username=data["username"]
	employee_id=data["employee_id"]
	password=data["password"]
	# DeviceLocalIP=GroupDevice.objects.get(group_id = data["group_id"])
	# active_status=devices= GroupDevice.objects.filter(group_id=data["group_id"]).values_list('active_status', flat=True)
	devices= GroupDevice.objects.filter(group_id=data["group_id"]).values_list('device_id', flat=True)
	train=[]
	i=0
	if id in devices:
		print("i=",i)
		i=i+1
		print("device id :",id)

		deviceip, deviceusername, devicepassword, deviceactivity = ghelp().getDeviceIpUsernamePassword(Devices, id)
		print("device info :",deviceip)
		
		flag=False
		try:
		
			if deviceactivity=="active" and is_device_active(deviceip):


				# print("ip : ",ip)

				###Add user info into dahua device
				print("inside loop registration date : ",reg_date)

				
				employee_add_info_url=f'http://{deviceip}/cgi-bin/recordUpdater.cgi?action=insert&name=AccessControlCard&CardName={username}&CardNo={cardno}&UserID={employee_id}&CardStatus=0&CardType=0&Password={password}&Doors[{0}]=0&VTOPosition=01018001&ValidDateStart={reg_date}%20093811&ValidDateEnd={valid_date}%20093811'
				response=requests.get(employee_add_info_url,auth=HTTPDigestAuth(deviceusername, devicepassword))
				print("response create employee:",response.url)


				###Dahua image add API

				# resize_image(image_path,image_path,80)
				with open(image_path,"rb") as image:
					im=image.read()
					# print("img :",im)
					base64_img=base64.b64encode(im)
					print("image base64 : ",base64_img.decode("utf-8"))
					add_image_url=f"http://{deviceip}/cgi-bin/FaceInfoManager.cgi?action=add"
					data={
						"UserID":employee_id,
						"Info":{
							"UserName":username,
							"PhotoData":[base64_img.decode("utf-8")]
						}

					}
					train_flag=False
					if len(train)>0:
						for p in train:
							if p['status']=='active' and p['ip']==deviceip and p['train']==True:
								train_flag=True
					if train_flag==False:
						response = requests.post(add_image_url,json=data,auth=HTTPDigestAuth(deviceusername, devicepassword),headers={"Content-Type":"application/json"})
						print("response add image:",response.text)
						print("response add image code:",response.status_code)
						if response.status_code==200:
							flag=True
					train.append({"ip":deviceip,"status":deviceactivity,"train":flag})
					
			else:
				train.append({"ip":deviceip,"status":deviceactivity,"train":False})
		except ConnectionAbortedError as e:
			print(e)
	print("trained list :",train)
