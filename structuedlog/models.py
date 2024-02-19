from django.db import models

from department.models import Department
from designation.models import Designation

# Create your models here.
class StructuredLog(models.Model):
	ID=models.AutoField(primary_key=True)
	device_id = models.ForeignKey("devices.Devices",on_delete=models.CASCADE)
	group_id=models.ForeignKey("empgrp.Group",on_delete=models.CASCADE)
	employee_id=models.ForeignKey("employee.Employee",on_delete=models.CASCADE,null=True)
	username = models.CharField(max_length=100,default="-",null=True)
	InTime=models.DateTimeField(null=True)
	department=models.ForeignKey("department.Department",on_delete=models.CASCADE,null=True)
	designation=models.ForeignKey("designation.Designation",on_delete=models.CASCADE,null=True)
	department_name = models.CharField(max_length=100, null=True, blank=True)
	designation_name = models.CharField(max_length=100, null=True, blank=True)
	def save(self, *args, **kwargs):
		# Fetch the corresponding Department and Designation instances
		if self.department_id:
			department_instance = Department.objects.get(pk=self.department_id)
			self.department_name = department_instance.department

		if self.designation_id:
			designation_instance = Designation.objects.get(pk=self.designation_id)
			self.designation_name = designation_instance.designation

		super().save(*args, **kwargs)



