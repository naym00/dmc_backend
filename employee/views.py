from helps.common.generic import Generichelps as ghelp
from datetime import datetime, timezone
from pydoc import stripid
from django.shortcuts import render
from django.conf import settings
from rest_framework.response import Response

from empgrp.models import Group
from shift_management.models import ShiftAssign, ShiftManagement
from .serializers import EmployeeSerializer,TrainEmployeeFromCSVSerializer
from .models import Employee, EmployeeGroupDevice
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import requests
import json
import base64
import os
from pathlib import Path
from devices.models import Devices
from . import models
from grpdev.models import GroupDevice
from requests.auth import HTTPDigestAuth
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import re
from urllib.parse import unquote
from PIL import Image
from rest_framework.pagination import PageNumberPagination
from devices.check_device_status import is_device_active
from designation.models import Designation
from department.models import Department
# Create your views here.

@api_view(['GET','POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def employee(request):
	print("request :",request)
	employee_id_filter = request.GET.get('employee_id', None)

	if request.method == 'GET':
		valid_column_accessor = ['employee_id', 'username', 'email', 'phone_number', 'shift_id', 'registration_date', 'validity_date', 'employee_type', 'group_id', 'department', 'designation', 'department_name', 'designation_name', 'shift_name', 'group_name']
		tasks = Employee.objects.all()
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
		else: tasks = tasks.order_by('-employee_id')

		serializer = EmployeeSerializer(tasks,many=True)
		paginator = PageNumberPagination()
		paginator.page_size = int(request.GET.get('page_size', 10))
		if employee_id_filter:
			tasks=tasks.filter(employee_id=employee_id_filter)

		result_page = paginator.paginate_queryset(tasks, request)
		serializer = EmployeeSerializer(result_page, many=True)
		return paginator.get_paginated_response(serializer.data)

	if request.method == 'POST':
		if request.data["group_id"]!=None:
			print("Request Data:", request.data)
			serializer = EmployeeSerializer(data=request.data)

			if serializer.is_valid():
				print("serializer group :",request.data["group_id"])

				serializer.save()


				employee = Employee.objects.get(employee_id=request.data['employee_id'])
				print("got employee ",employee)
				print("before hashing : ",employee.password)

				employee.password = make_password(employee.password)
				print("hashed password : ",employee.password)
				employee.save()
				# Set the hashed password for the specific Employee instance
				print("Saved Data:", serializer.data)
				all_data=serializer.data
				
				group_name=Group.objects.filter(group_id=request.data["group_id"]).values_list("group_name",flat=False)
				employee.group_name=group_name[0][0]
				after_serialize=EmployeeSerializer(employee)





				##this portion should be uncomment during employee adding into the device	
				print("all data :",all_data)		

				if all_data["group_id"] != None and all_data["image"]==None:
					train_employee(all_data)
				elif all_data["group_id"] != None and all_data["image"]!=None:
					train_employee_with_image(all_data)
				print("employee_id :",all_data['employee_id']," ,shift_id :",all_data["shift_id"])
				shift_id=ShiftManagement.objects.get(shift_id=all_data["shift_id"])
				print("shift_id instance : ",shift_id)
				emp_ins=Employee.objects.get(employee_id = all_data['employee_id'])

				
				shift_assign=ShiftAssign(employee_id=emp_ins,shift_id=shift_id)
				shift_assign.save()
				print("shift assigned !!!")

				return Response(after_serialize.data, status=status.HTTP_201_CREATED)
			else:
				print("Errors:", serializer.errors)
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		else:
			print("Request Data:", request.data)
			serializer = EmployeeSerializer(data=request.data)

			if serializer.is_valid():
				print("serializer group :",request.data["group_id"])

				serializer.save()


				employee = Employee.objects.get(employee_id=request.data['employee_id'])
				print("got employee ",employee)
				print("before hashing : ",employee.password)

				employee.password = make_password(employee.password)
				print("hashed password : ",employee.password)
				employee.save()
				# Set the hashed password for the specific Employee instance
				print("Saved Data:", serializer.data)
				all_data=serializer.data
				
				group_name=Group.objects.filter(group_id=request.data["group_id"]).values_list("group_name",flat=False)
				employee.group_name=group_name[0][0]
				after_serialize=EmployeeSerializer(employee)





				##this portion should be uncomment during employee adding into the device	
				print("all data :",all_data)		

				# if all_data["group_id"] != None and all_data["image"]==None:
				# 	train_employee(all_data)
				# elif all_data["group_id"] != None and all_data["image"]!=None:
				# 	train_employee_with_image(all_data)
				print("employee_id :",all_data['employee_id']," ,shift_id :",all_data["shift_id"])
				shift_id=ShiftManagement.objects.get(shift_id=all_data["shift_id"])
				print("shift_id instance : ",shift_id)
				emp_ins=Employee.objects.get(employee_id = all_data['employee_id'])

				
				shift_assign=ShiftAssign(employee_id=emp_ins,shift_id=shift_id)
				shift_assign.save()
				print("shift assigned !!!")

				return Response(after_serialize.data, status=status.HTTP_201_CREATED)
			else:
				print("Errors:", serializer.errors)
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	else:
		return Response({"message":"Group id must be given"}, status=status.HTTP_400_BAD_REQUEST)

	# if request.method == 'POST' and request.FILES['image']:
	# 	image_file = request.FILES['image']
	# 	print('Image File :',image_file)
	# 	file_path = default_storage.save('images/' + image_file.name, ContentFile(image_file.read()))
	# 	user = Employee.objects.create(username=request.data['username'], image=file_path)
	# 	return Response({'message': 'Image uploaded successfully.'})

@api_view(['GET','POST','DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def employee_with_id(request,pk):
	task = Employee.objects.filter(employee_id=pk).first()
	if task!=None:
		print("task : ",task)
		checker = EmployeeSerializer(task, many=False)
		checker_data=checker.data
		if request.method == 'GET' :
			serializer = EmployeeSerializer(task, many=False)
			# hashed=make_password("1234") 
			# # if hashed == serializer.data["password"]:
			# print("hashed :",hashed,"password is : 1234")
					# Input string

			timestamp_str = serializer.data["UniqueCardNumber"]

			# Convert string to datetime object
			timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z")

			# Convert datetime object to timestamp (seconds since the epoch)
			timestamp_seconds = timestamp_dt.timestamp()
			timestamp_milliseconds = int(timestamp_seconds * 1000)
			print(timestamp_milliseconds)
			print("timestamp_mili seconds : ",timestamp_milliseconds)
			# get_employee_data(serializer.data)


			# serializer.data["UniqueCardNumber"]=int(timestamp_milliseconds)
			# print("miliseconds data : ",serializer.data["UniqueCardNumber"])

			return Response(serializer.data)

		if request.method == 'POST' :
			# {'employee_id': 'DMC9', 'shift_id': 5, 'is_active': True, 'designation': 1, 'department': 1, 'group_id': 1}
			previous_group_id = int(task.group_id.group_id) if task.group_id else None
			new_group_id = None
			device_flag = False

			designation_id = request.data.get('designation')
			department_id = request.data.get('department')
			group_id = request.data.get('group_id')
			shift_id = request.data.get('shift_id')
			image = request.FILES.get('image')

			if designation_id:
				if not ghelp().checkExistence(Designation, {'id': designation_id}): del request.data['designation']
			if department_id:
				if not ghelp().checkExistence(Department, {'id': department_id}): del request.data['department']
			if group_id:
				if not ghelp().checkExistence(Group, {'group_id': group_id}): del request.data['group_id']
				else:
					device_flag = True
					new_group_id = int(request.data['group_id'])
					request.data.update({'group_name': Group.objects.get(group_id=group_id).group_name})
			else: new_group_id = previous_group_id
			if shift_id:
				if not ghelp().checkExistence(ShiftManagement, {'shift_id': shift_id}): del request.data['shift_id']
			if image:
				if not ghelp().validatejpgimg(str(image)):
					del request.data['image']
				else:
					device_flag = True
					if os.path.exists(task.image.path): os.remove(task.image.path)

			serializer = EmployeeSerializer(instance=task, data=request.data, partial=True)
			if serializer.is_valid():
				serializer.save()

				employee = Employee.objects.filter(employee_id=pk).first()

				if device_flag: ghelp().change_group_image(GroupDevice, Devices, previous_group_id, new_group_id, employee)

				print("got employee ",employee)
				print("before hashing : ",employee.password)

				employee.password = make_password(employee.password)
				print("hashed password : ",employee.password)
				employee.save()
				
				after_serialize=EmployeeSerializer(instance=employee,many=False,partial=True)

				# if after_serialize.is_valid():
				# 	after_serialize.save()

				return Response(after_serialize.data)
			else:
				return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
		elif request.method == 'DELETE' :
				### This portion will uncomment during actual employee train and testing
				try:
					delete_info(pk)
					task.delete()
					return Response({"message":"employee successfully deleted!"})
				except Exception as e:
					print("excedption :",e)
					return Response({"message":e})
	else:
		return Response({"message":"Employee id is not valid"})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_from_csv(request):
    data=request.data["file"]
    file=TrainEmployeeFromCSVSerializer(data)
    print("file :",data)
    # Specify the file path
    csv_file_path = 'your_file.csv'

    # Open the CSV file
    with open(csv_file_path, 'r') as file:
        # Create a CSV reader
        csv_reader = csv.reader(file)

        # Iterate through each row in the CSV file
        for row in csv_reader:
            # Access individual elements in each row
            print(row)

def add_image(data):
	print("E_ID :",data['employee_id'])
	print("Name :",data["username"])
	print("Surname",data["username"].replace(" ","_"))
	# image_path = os.path.join(settings.MEDIA_ROOT, str(employee.employee_id), "image.jpg")
	img=data["image"].replace("/media","")
	# img=img.replace("/","\\")
	# image_path = os.path.join(settings.MEDIA_ROOT,data['employee_id'],data["username"]+".jpg")
	img = img.lstrip('/')
	image_path = Path(settings.MEDIA_ROOT) / img
	print("img :",img)
	print("media root :",settings.MEDIA_ROOT)
	print("image path :",image_path)
	print("register date : ",data["registration_date"])
	print("validity_date :",data["validity_date"])
	# DeviceLocalIP=GroupDevice.objects.get(group_id = data["group_id"])
	devices= GroupDevice.objects.filter(group_id=data["group_id"]).values_list('device_id', flat=True)
	i=0
	resize_image(image_path,image_path,80)
	for dev in devices:
		print("i=",i)
		i=i+1
		print("dev :",dev)
		deviceip, deviceusername, devicepassword, deviceactivity = ghelp().getDeviceIpUsernamePassword(Devices, dev)
		if deviceactivity=="active" and is_device_active(deviceip):

			print("ip : ",deviceip)

			###Add user info into dahua device
			reg_date=data["registration_date"]
			reg_date=reg_date.replace("-","")
			valid_date=data["validity_date"]
			valid_date=valid_date.replace("-","")
			###Dahua image add API

			
			with open(image_path,"rb") as image:
				im=image.read()
				# print("img :",im)
				base64_img=base64.b64encode(im)
				# print("image base64 : ",base64_img.decode("utf-8"))
				add_image_url=f"http://{deviceip}/cgi-bin/FaceInfoManager.cgi?action=add"
				data={
					"UserID":data["employee_id"],
					"Info":{
						"UserName":data["username"],
						"PhotoData":[base64_img.decode("utf-8")]
					}

				}
				response = requests.post(add_image_url,json=data,auth=HTTPDigestAuth(deviceusername, devicepassword),headers={"Content-Type":"application/json"})
				print("response add image:",response.text)

	return 

		
def get_employee_data(data):
		devices= GroupDevice.objects.filter(group_id=data["group_id"]).values_list('device_id', flat=True)
		for dev in devices:
			deviceip, deviceusername, devicepassword, deviceactivity = ghelp().getDeviceIpUsernamePassword(Devices, dev)
			url=f"http://{deviceip}/cgi-bin/recordFinder.cgi?action=find&name=AccessControlCard&condition.UserID={data['employee_id']}&count=100"
			resp=requests.get(url,auth=HTTPDigestAuth(deviceusername, devicepassword))
			print("response :",resp.text)
			data=resp.text.split('\n')
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
			print("records :",records)
			with open("people.txt","w") as file:
				file.write(str(resp.text))
			# log_records=[]
			# log_records.append(current_record)

			for index in range(len(records)):
				print("---for index---- : ",index)
				# print("AttendanceState : ",records[index]['AttendanceState'])
				print("CardName : ",records[index]['CardName'])
				print("CardNo : ",records[index]['CardNo'])

				print("Password: ",records[index]['Password'])
				print("RecNo : ",records[index]['RecNo'])
				print("UserID : ",records[index]['UserID'])

				return records[index]['RecNo']
			

def train_employee(data):
	print("E_ID :",data['employee_id'])
	print("Name :",data["username"])
	print("Surname",data["username"].replace(" ","_"))

	print("register date : ",data["registration_date"])
	print("validity_date :",data["validity_date"])
	# DeviceLocalIP=GroupDevice.objects.get(group_id = data["group_id"])
	devices= GroupDevice.objects.filter(group_id=data["group_id"]).values_list('device_id', flat=True)
	i=0
	for dev in devices:
		print("i=",i)
		i=i+1
		print("dev :",dev)
		deviceip, deviceusername, devicepassword, deviceactivity = ghelp().getDeviceIpUsernamePassword(Devices, dev)
		# for ip in DeviceLocalIP:
		if deviceactivity=="active" and is_device_active(deviceip):
			print("ip found: ",deviceip)

			###Add user info into dahua device
			reg_date=data["registration_date"]
			reg_date=reg_date.replace("-","")
			valid_date=data["validity_date"]
			valid_date=valid_date.replace("-","")
			try:
				employee_add_info_url=f'http://{deviceip}/cgi-bin/recordUpdater.cgi?action=insert&name=AccessControlCard&CardName={data["username"]}&CardNo={data["cardNo"]}&UserID={data["employee_id"]}&CardStatus=0&CardType=0&Password={data["password"]}&Doors[0]=0&VTOPosition=01018001&ValidDateStart={reg_date}%20093811&ValidDateEnd={valid_date}%20093811'
				response=requests.get(employee_add_info_url,auth=HTTPDigestAuth(deviceusername, devicepassword))
				print("response create employee:",response)
			except ConnectionError as e:
				print("error :",e)



def train_employee_with_image(data):
	print("data for training :",data)
	print("E_ID :",data['employee_id'])
	print("Name :",data["username"])
	print("Surname",data["username"].replace(" ","_"))
	# image_path = os.path.join(settings.MEDIA_ROOT, str(employee.employee_id), "image.jpg")
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
	reg_date=data['registration_date']
	reg_date=reg_date.replace("-","")
	valid_date=data["validity_date"]
	valid_date=valid_date.replace("-","")
	cardno=int(data["cardNo"])
	username=data["username"]
	employee_id=data["employee_id"]
	password=data["password"]
	# DeviceLocalIP=GroupDevice.objects.get(group_id = data["group_id"])
	# active_status=devices= GroupDevice.objects.filter(group_id=data["group_id"]).values_list('active_status', flat=True)
	devices= GroupDevice.objects.filter(group_id=data["group_id"]).values_list('device_id', flat=True)
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
		
		print("found ip :",deviceip," and status :",deviceactivity)
		flag=False
		c=0
		try:
		
			if deviceactivity=="active" and is_device_active(deviceip):


				# print("ip : ",ip)

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
				c+=1
			if c>0:
				employee_ins=Employee.objects.get(employee_id=employee_id)
				group_ins=Group.objects.get(group_id=group_id)
				dev_ins=Devices.objects.get(device_id=dev)

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




def update_data(data):
	devices= GroupDevice.objects.filter(group_id=data["group_id"]).values_list('device_id', flat=True)
	i=0
	for dev in devices:
		print("i=",i)
		i=i+1
		print("dev :",dev)
		deviceip, deviceusername, devicepassword, deviceactivity = ghelp().getDeviceIpUsernamePassword(Devices, dev)
		print("device info :",deviceip)
		
		flag=False




		EmployeeName = data["username"]
		
		EmployeeID = data["employee_id"]
		Password=data["password"] 

		print("DeviceLocalIP :",deviceip)
		print("EmployeeName : ",EmployeeName)
		print("EmployeeID : ",EmployeeID)
		print("Password : ",Password)
		if deviceactivity=="active" and is_device_active(deviceip):

			RecordNumberFrom_Find_Employee_Info=int(get_record_number(deviceip, EmployeeID, deviceusername, devicepassword))
			print("ip :",deviceip)


			door = '&Doors[0]=0'
			door_decoded = unquote(door)
			update_info=f"http://{deviceip}/cgi-bin/recordUpdater.cgi?action=update&name=AccessControlCard&recno={RecordNumberFrom_Find_Employee_Info}&CardName={EmployeeName}&CardNo={data['cardNo']}&UserID={EmployeeID}&CardStatus=0&CardType=0&Password={Password}&Doors[{0}]=0"
			
			response = requests.get(update_info,auth=HTTPDigestAuth(deviceusername, devicepassword))
			print("update_info_url :  ",response.url)

			print("response update info: ",response.text)

def get_record_number(ip,employee_id, deviceusername, devicepassword):
		find_employee_info_url=f"http://{ip}/cgi-bin/recordFinder.cgi?action=find&name=AccessControlCard&condition.UserID={employee_id}&count={8000}"
		resp=requests.get(find_employee_info_url,auth=HTTPDigestAuth(deviceusername, devicepassword))
		print("find user url : ",resp.url)
		print("response :",resp.text)

		data_1=resp.text.split('\n')
		records = []

		# Split the text into lines
		lines = data_1

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
		print("cardNo :",records[0]["CardNo"])
		print("RecNo :",records[0]["RecNo"])
		return records[0]["RecNo"]
		

def delete_info(e_id):
	info=Employee.objects.get(employee_id=e_id)
	serializer = EmployeeSerializer(info, many=False)
	data=serializer.data
	devices=GroupDevice.objects.filter(group_id=data["group_id"]).values_list("device_id",flat=True)
	for dev in devices:
		print("dev : ",dev)
		c=0

		deviceip, deviceusername, devicepassword, deviceactivity = ghelp().getDeviceIpUsernamePassword(Devices, dev)

		if deviceactivity=="active" and is_device_active(deviceip):
			ind_employee_info_url=f"http://{deviceip}/cgi-bin/recordFinder.cgi?action=find&name=AccessControlCard&condition.UserID={data['employee_id']}&count={8000}"
			resp=requests.get(find_employee_info_url,auth=HTTPDigestAuth(deviceusername, devicepassword))
			print("response :",resp.text)

			r=resp.text
			r=r.replace("found=","")
			print("num of rec found :",r)
			# n=int(r)
			# print("n = ",n)
			match = re.search(r'found=(\d+)', resp.text)
			n=0
			if match:
				foundf_value = match.group(1)
				print(f"Found value: {found_value}")
				n=int(found_value)
			else:
				print("No 'found' value found.")
			
			if n>0:
			### RecordNumberFrom_Find_Employee_Info should be retrieve from 'resp.text'
				RecordNumberFrom_Find_Employee_Info=int(get_record_number(deviceip, data['employee_id'], deviceusername, devicepassword)) #for testing ,suppose RecordNumberFrom_Find_Employee_Info=45
				

				employee_delete_url=f"http://{deviceip}/cgi-bin/recordUpdater.cgi?action=remove&name=AccessControlCard&recno={RecordNumberFrom_Find_Employee_Info}"
				response= requests.get(employee_delete_url,auth=HTTPDigestAuth(deviceusername, devicepassword))
				print("delete response : ",response.text)
			else:
				# emp_dev_train=EmployeeGroupDevice(
				# 	employee_id=data['employee_id'],
				# 	group_id=data["group_id"],
				# 	device_id=dev,
				# 	action="delete"
					
					
				# )
				employee_ins=Employee.objects.get(employee_id=data['employee_id'])
				group_ins=Group.objects.get(group_id=data["group_id"])
				dev_ins=Devices.objects.get(device_id=dev)

				emp_dev_train=EmployeeGroupDevice(
					employee_id=employee_ins,
					device_id=dev_ins,
					action="delete"
					
					
				)
				emp_dev_train.save()
				###this action("delete") should be addred in EmployeeGroupDevice table
				print("this action=delete should be addred in EmployeeGroupDevice table")



def resize_image(input_path,output_path,max_size_kb):
	try:
		with Image.open(input_path) as img:
			original_size = os.path.getsize(input_path)
			original_width, original_height = img.size
			target_size_bytes = max_size_kb * 1024
			scale_factor = 1.0
			if original_size > target_size_bytes:
				scale_factor = (target_size_bytes / original_size) ** 0.5

			new_width = int(original_width * scale_factor)
			new_height = int(original_height * scale_factor)
			resized_img = img.resize((new_width, new_height), Image.LANCZOS)
			resized_img.thumbnail((230, 230)) 
			resized_img.save(output_path, optimize=True, quality=100)
			print("compressing ...")
	except MemoryError as e:
		print("not compressed :",e)
		
	
	return Response({"message":"compressed successfully"})


def pagination():
			if "&" in id:
				flag=1
				print("id :",id)
				pageNo=id.split('&')[0]
				dataNo=id.split('&')[1]
				print("pageNo :",pageNo,"dataNo :",dataNo)
				pageCount=pageNo.split('=')[1]
				dataCount=dataNo.split('=')[1]
				print("pageCount :",pageCount,"dataCount :",dataCount)
				print("data from :",(int(pageCount)-1)*int(dataCount),"data to ",int(pageCount)*int(dataCount))
			
			rangeBegin=(int(pageCount)-1)*int(dataCount)
			rangeEnd=int(pageCount)*int(dataCount)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_employee_info_from_mis(request,pk):
	id=pk
	data={
    "employee_id": id,
    "last_login": None,
    "is_superuser": False,
    "is_staff": True,
    "is_active": True,
    "username": "pronoy",
    "email": "-",
    "phone_number": "-",
    "employee_type": "user",
    "shift": "morning",
    "department": "gynocology",
    "designation": "gynocologist"
}


	return Response({"message":data})