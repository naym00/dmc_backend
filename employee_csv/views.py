# myapp/views.py
from helps.common.generic import Generichelps as ghelp
import base64
import os
from pathlib import Path
from django.shortcuts import get_object_or_404
import requests
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import csv
import zipfile
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import datetime, timedelta
from department.models import Department
from designation.models import Designation
from devices.check_device_status import is_device_active
from devices.models import Devices
from dmc import settings
from employee.models import Employee, EmployeeGroupDevice, resize_image
from employee.serializers import EmployeeSerializer
from io import BytesIO
from django.core.files.base import ContentFile
from grpdev.models import GroupDevice
from shift_management.models import ShiftManagement
from empgrp.models import Group
from requests.auth import HTTPDigestAuth


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def file_upload_view(request, format=None):
	if 'zip_file' in request.data and 'csv_file' in  request.data:
		if request.method == 'POST':
			# Parse CSV file
			csv_file = request.FILES['csv_file']
			csv_data = csv.reader(csv_file.read().decode('utf-8').splitlines())
			# for employee_data in csv_data:
			#     print("employee info:")
			#     for i in range(7):
			#         print(employee_data[i])


			# Extract ZIP file
			zip_file = request.FILES['zip_file']
			with zipfile.ZipFile(zip_file, 'r') as z:
				i=0
				for employee_data in csv_data:
					if i>0:
						employee_id = employee_data[0]
						image_filename = f'employee_images/{employee_id}.jpg'
						print("employeeimage name :",image_filename)
						if image_filename in z.namelist():
							try:
								image_data = z.read(image_filename)
								# print("image data:",image_data)
								base64_encoded = base64.b64encode(image_data).decode('utf-8')
								# print("base64 img:",base64_encoded)
								print("employee info :",employee_data)
												# Save the image to the model's ImageField
								
								instance = Employee()
								instance.employee_id = employee_id # Set other model fields as needed
								instance.username=employee_data[1]
								instance.email=employee_data[2]
								instance.password=make_password(employee_data[3])
								instance.phone_number=employee_data[4]
								check_shift=ShiftManagement.objects.filter(shift_id=employee_data[5]).first()
								if check_shift==None:
									return Response({"message":"shift does not exist"}, status=status.HTTP_400_BAD_REQUEST)
								
								shift_ins=ShiftManagement.objects.filter(shift_id=employee_data[5])
								
								instance.shift_id=shift_ins[0]
								check_group=Group.objects.filter(group_id=employee_data[6]).first()
								if check_group==None:
									return Response({"message":"shift does not exist"}, status=status.HTTP_400_BAD_REQUEST)

								group_ins=Group.objects.filter(group_id=employee_data[6])
								instance.group_id=group_ins[0]
								check_designation=Designation.objects.filter(id=employee_data[7]).first()
								if check_designation==None:
									return Response({"message":"designation does not exist"}, status=status.HTTP_400_BAD_REQUEST)
								
								if check_department==None:
									return Response({"message":"department does not exist"}, status=status.HTTP_400_BAD_REQUEST)
								

								



								check_department=Department.objects.filter(id=employee_data[8]).first()


								



								# Save the image to the model's ImageField
								instance.image.save(employee_data[1]+".jpg", ContentFile(image_data), save=True)
								path_link = instance.image.url
								print("Path Link:", path_link)
								# Optionally, encode image to base64
								base64_encoded = base64.b64encode(image_data).decode('utf-8')
								print("Base64 encoded image:", base64_encoded)
								# Set other model fields based on employee_data
								
								instance.save()
								reg_date=datetime.now()
								valid_date=datetime.now() + timedelta(days=5*365)
								
								data={
									'group_id':employee_data[6],
									'username':employee_data[1],
									'cardNo':int(reg_date.timestamp()*1000),
									'employee_id':employee_id,
									'password':employee_data[3],
									'reg_date':reg_date,
									'valid_date':valid_date,
									'image':path_link
									}
								train_employee(data)
								print("data :",data)
							except KeyError as e:
								return  Response({'message': 'Please recheck your file info.group id ,shift id,designation id,department id should be in the database','uploaded':False}, status=status.HTTP_400_BAD_REQUEST)
						else:
							return  Response({'message': 'Zip image name ,should be user id and csv employee_id and zip image name should be same ','uploaded':False}, status=status.HTTP_400_BAD_REQUEST)

					i+=1

			return Response({'message': 'Upload successful','uploaded':True}, status=status.HTTP_201_CREATED)

		return Response({'message': 'Invalid request','uploaded':False}, status=status.HTTP_400_BAD_REQUEST)
	else:
		return Response({"message":"zip_file  and csv_file both name and file should be exist !!",'uploaded':False})

def train_employee(data):
	print("E_ID :",data['employee_id'])
	print("Name :",data["username"])
	print("Surname",data["username"].replace(" ","_"))
	# image_path = os.path.join(settings.MEDIA_ROOT, str(employee.employee_id), "image.jpg")
	img=data["image"]
	# img=img.replace("/","\\")
	# image_path = os.path.join(settings.MEDIA_ROOT,data['employee_id'],data["username"]+".jpg")
	img=data["image"].replace("/media","")
	img=img.replace("/","\\")
	# image_path = os.path.join(settings.MEDIA_ROOT,data['employee_id'],data["username"]+".jpg")

	# img = img.lstrip('/')
	print("image path :",img)
	image_path = str(settings.MEDIA_ROOT) + img
	print("final image path :",image_path)

	# print("img :",img)
	# print("media root :",settings.MEDIA_ROOT)
	# print("image path :",image_path)
	# print("inside train :",data)
	# print("register date : ",data['registration_date'])
	# print("validity_date :",data["validity_date"])
	reg_date=data['reg_date']
	print("reg date :",reg_date)
	reg_date=reg_date.strftime("%Y%m%d")
	valid_date=data["valid_date"]
	valid_date=valid_date.strftime("%Y%m%d")
	print("cardNo :",data["cardNo"])
	cardno=int(data["cardNo"])
	username=data["username"]
	employee_id=data["employee_id"]
	password=data["password"]
	print("group_id :",data["group_id"])
	# DeviceLocalIP=GroupDevice.objects.get(group_id = data["group_id"])
	# active_status=devices= GroupDevice.objects.filter(group_id=data["group_id"]).values_list('active_status', flat=True)
	group_instance=Group.objects.get(group_id=data["group_id"])
	print("group_instance :",group_instance)
	devices= GroupDevice.objects.filter(group_id=group_instance).values_list('device_id', flat=True)
	print("devices :",devices)
	train=[]
	group_id=data["group_id"]
	i=0
	not_inserted_devices=[]
	print("total devices :",devices.count())
	for dev in devices:
		print("i=",i)
		i=i+1
		print("dev :",dev)
		deviceip, deviceusername, devicepassword, deviceactivity = ghelp().getDeviceIpUsernamePassword(Devices, dev)
		print("device info :",deviceip)
		
		flag=False
		c=0
		try:
		
			if deviceactivity=="active" and is_device_active(deviceip):


				# print("deviceip : ",deviceip)

				###Add user info into dahua device
				print("inside loop registration date : ",reg_date)

				
				employee_add_info_url=f'http://{deviceip}/cgi-bin/recordUpdater.cgi?action=insert&name=AccessControlCard&CardName={username}&CardNo={cardno}&UserID={employee_id}&CardStatus=0&CardType=0&Password={password}&Doors[{0}]=0&VTOPosition=01018001&ValidDateStart={reg_date}%20093811&ValidDateEnd={valid_date}%20093811'
				response=requests.get(employee_add_info_url,auth=HTTPDigestAuth(deviceusername, devicepassword))
				print("response create employee:",response.url)
				if response.status_code>=200 and response.status_code<299:
					print("added info to device")
				else:
					c=c+1


				###Dahua image add API

				resize_image(image_path,image_path,80)
				with open(image_path,"rb") as image:
					im=image.read()
					# print("img :",im)
					base64_img=base64.b64encode(im)
					# print("image base64 : ",base64_img.decode("utf-8"))
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
						if response.status_code>=200 and response.status_code<=299:
							flag=True
						else:
							c+=1
							
					train.append({"ip":deviceip,"status":deviceactivity,"train":flag})
					if c>0:
						not_inserted_devices.append(dev)
					
			else:
				train.append({"ip":deviceip,"status":deviceactivity,"train":False})
				not_inserted_devices.append(dev)

			if c>0:
				employee_ins=Employee.objects.get(employee_id=employee_id)
				group_ins=Group.objects.filter(group_id=group_id)
				group_instance = get_object_or_404(Group, group_id=group_id)
				dev_ins=Devices.objects.get(device_id=dev)
				print("group_instance :",group_instance)
				print("group_ins :",group_ins[0])

				emp_dev_train=EmployeeGroupDevice(
					employee_id=employee_ins,
					device_id=dev_ins,
					action="add"
					
					
				)
				emp_dev_train.save()
		except ConnectionAbortedError as e:
			print(e)
	print("trained list :",train)
	return not_inserted_devices