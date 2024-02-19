from datetime import datetime
from django.db import models
from django.utils import timezone
from department.models import Department
from designation.models import Designation

# Create your models here.
class Log(models.Model):
	r_clsf_record_id=models.AutoField(primary_key=True)
	device_id = models.ForeignKey("devices.Devices",on_delete=models.CASCADE)
	CardName = models.CharField(max_length=100,default="-",null=True)
	InTime=models.DateTimeField(null=True)
	RecNo=models.IntegerField(default=0,null=True)
	RoomNumber=models.CharField(default="-",null=True,max_length=100)
	Status=models.IntegerField(default=0,null=True)
	Type=models.CharField(default="-",null=True,max_length=100)
	image_url=models.CharField(max_length=100,default="-",null=True)
	employee_id=models.ForeignKey("employee.Employee",on_delete=models.CASCADE,null=True)
	department=models.ForeignKey("department.Department",on_delete=models.CASCADE,null=True)
	designation=models.ForeignKey("designation.Designation",on_delete=models.CASCADE,null=True)
	department_name = models.CharField(max_length=100, null=True, blank=True)
	designation_name = models.CharField(max_length=100, null=True, blank=True)
	last_synced=models.BooleanField(null=True,default=False)
	logdate = models.DateField(null=True, default=timezone.now)

	def save(self, *args, **kwargs):
		# Fetch the corresponding Department and Designation instances
		if self.department_id:
			department_instance = Department.objects.get(pk=self.department_id)
			self.department_name = department_instance.department

		if self.designation_id:
			designation_instance = Designation.objects.get(pk=self.designation_id)
			self.designation_name = designation_instance.designation

		super().save(*args, **kwargs)



