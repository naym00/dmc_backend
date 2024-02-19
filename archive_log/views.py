import csv
from datetime import datetime,timedelta

import os
from django.shortcuts import render
from rest_framework.response import Response
from attendance_report.models import AttendanceReport
from django.utils import timezone

from dmc.settings import MEDIA_DIR
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import shutil
from employee.models import Employee

from log.models import Log
from login.models import LogInLog
from structuedlog.models import StructuredLog
from .models import Archivelog

# Create your views here.
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])

def delete_previous_log_data(request):
	logintoken=request.headers['Authorization']
	logintoken=logintoken.replace("Bearer ","")
	employee_id_found=LogInLog.objects.filter(token=str(logintoken)).values_list("employee_id",flat=True)
	print("login token :",logintoken)
	print("loged in employee :",employee_id_found[0])

	try:
		##delete attendance log
			#  {
			#     "ID": 223,
			#     "username": "rezvi",
			#     "InTime": "2023-12-24T22:20:42+06:00",
			#     "OutTime": "2023-12-24T22:20:42+06:00",
			#     "total_work_minutes": 0,
			#     "cumalative_work_minutes": 0,
			#     "device_id": "DmcGate10",
			#     "group_id": 2,
			#     "employee_id": "1"
			# }


		six_months_ago = timezone.now() - timezone.timedelta(minutes=6)
		t_string=str(timezone.now())
		time_string=t_string.replace(" ","_").replace(".","_").replace("+","_").replace(":","_")
		print("time_string :",time_string)

		# Filter logs older than 6 months
		logs_to_delete = AttendanceReport.objects.filter(InTime__lt=six_months_ago)

		# Export to CSV
		csv_filename = f'old_attendance_logs_till_{time_string}_backup.csv'
		with open(csv_filename, 'w', newline='') as csvfile:
			fieldnames = ['ID', 'username', 'InTime','OutTime','total_work_minutes','cumalative_work_minutes','device_id','group_id','employee_id']  # Replace with actual field names
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

			# Write CSV header
			writer.writeheader()

			# Write log data to CSV
			for log in logs_to_delete:
				writer.writerow({'ID':log.ID, 'username':log.username, 'InTime':log.InTime,'OutTime':log.OutTime,'total_work_minutes':log.total_work_minutes,'cumalative_work_minutes':log.cumalative_work_minutes,'device_id':log.device_id,'group_id':log.group_id,'employee_id':log.employee_id})  # Replace with actual field values

		# Delete logs
		logs_to_delete.delete()
		path=str(MEDIA_DIR)+f'/logs/{csv_filename}'
		# Optionally, move the CSV file to a desired location
		print("path :",path)
		os.rename(csv_filename, path)
		# shutil.move(csv_filename, path)

		
	### raw_log delete
		##delete attendance log
			# {
			#     "r_clsf_record_id": 238,
			#     "CardName": "tanim_Test",
			#     "InTime": "2023-12-25T00:46:04+06:00",
			#     "RecNo": 238,
			#     "RoomNumber": "",
			#     "Status": 1,
			#     "Type": "Entry",
			#     "image_url": "/SnapShotFilePath/2023-12-24/20/46/DMC653_99_100_20231224204604792.jpg",
			#     "device_id": "DmcGate10",
			#     "employee_id": "DMC653"
			# }



		# Filter logs older than 6 months
		rlogs_to_delete = Log.objects.filter(InTime__lt=six_months_ago)

		# Export to CSV
		rcsv_filename = f'old_raw_logs_till_{time_string}_backup.csv'
		with open(rcsv_filename, 'w', newline='') as csvfile:
			fieldnames = ['r_clsf_record_id', 'CardName', 'InTime','RecNo','RoomNumber','Status','Type','image_url','device_id','employee_id']  # Replace with actual field names
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

			# Write CSV header
			writer.writeheader()

			# Write log data to CSV
			for log in rlogs_to_delete:
				writer.writerow({'r_clsf_record_id':log.r_clsf_record_id, 'CardName':log.CardName, 'InTime':log.InTime,'RecNo':log.RecNo,'RoomNumber':log.RoomNumber,'Status':log.Status,'Type':log.Type,'image_url':log.image_url,'device_id':log.device_id,'employee_id':log.employee_id})  # Replace with actual field values

		# Delete logs
		rlogs_to_delete.delete()
		path=str(MEDIA_DIR)+f'/logs/{rcsv_filename}'
		# Optionally, move the CSV file to a desired location
		print("path :",path)
		os.rename(rcsv_filename, path)	
		# shutil.move(rcsv_filename, path)


	### structured_log delete
		##delete attendance log
			# {
			#     "ID": 238,
			#     "username": "tanim_Test",
			#     "InTime": "2023-12-25T00:46:04+06:00",
			#     "device_id": "DmcGate10",
			#     "group_id": 2,
			#     "employee_id": "DMC653"
			# }



		# Filter logs older than 6 months
		slogs_to_delete = StructuredLog.objects.filter(InTime__lt=six_months_ago)

		# Export to CSV
		scsv_filename = f'old_structured_logs_till_{time_string}_backup.csv'
		with open(scsv_filename, 'w', newline='') as csvfile:
			fieldnames = ['ID', 'username', 'InTime','device_id','group_id','employee_id']  # Replace with actual field names
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

			# Write CSV header
			writer.writeheader()

			# Write log data to CSV
			for log in slogs_to_delete:
				writer.writerow({'ID':log.ID, 'username':log.username, 'InTime':log.InTime,'device_id':log.device_id,'group_id':log.group_id,'employee_id':log.employee_id})  # Replace with actual field values

		# Delete logs
		slogs_to_delete.delete()
		path=str(MEDIA_DIR)+f'/logs/{scsv_filename}'
		# Optionally, move the CSV file to a desired location
		print("path :",path)
		os.rename(scsv_filename, path)
		# shutil.move(scsv_filename, path)
		archive_time=timezone.now()+timedelta(hours=6)
		print("archive_time :",archive_time)
		employee_ins=Employee.objects.filter(employee_id=employee_id_found[0])
		archive=Archivelog(
			archive_time=archive_time,
			employee_id=employee_ins[0]
			)
		archive.save()
		return Response({"message":"log data successfully archived","archive_time":archive_time})


	
	
	except ConnectionAbortedError as e:
		return Response({"message":e})