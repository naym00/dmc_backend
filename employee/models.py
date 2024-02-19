from django.db import models
from datetime import datetime, timedelta, timezone
from django.shortcuts import get_object_or_404
from django.utils import timezone
from department.models import Department
from designation.models import Designation

from empgrp.models import Group
from devices.models import Devices
from shift_management.models import ShiftManagement 
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.hashers import make_password
from PIL import Image
import os
from django.core.exceptions import ObjectDoesNotExist
def get_default_date():
    return datetime.now().date() + timedelta(days=5*365)

def upload_user_image(instance,filename):
    return "{employee_id}/images/{filename}".format(employee_id=instance.employee_id,filename=filename)

def get_timestamp():
    return int(timezone.now().timestamp() * 1000)


def resize_image(input_path,output_path,max_size_kb):
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


class EmployeeGroup(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class EmployeePermission(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)


class Employee(AbstractUser):
    employee_id = models.CharField(max_length=100, primary_key=True,null=False,unique=True)
    username = models.CharField(max_length=100, null=False)
    first_name=None
    last_name=None
    email = models.CharField(max_length=100, null=True,default='-')
    password = models.CharField(max_length=100, null=True, default='-')
    phone_number = models.CharField(max_length=100, null=True, default='-')
    image_location = models.CharField(max_length=100, null=True,default='-')
    shift_id=models.ForeignKey("shift_management.ShiftManagement",on_delete=models.CASCADE,default=1,null=False)
    registration_date = models.DateField(null=True,auto_now_add=True)
    validity_date = models.CharField(max_length=100, null=True, default=get_default_date)
    employee_type = models.CharField(max_length=100, null=True, default='user')
    group_id = models.ForeignKey("empgrp.Group",on_delete=models.CASCADE,null=True)
    image =models.ImageField(upload_to=upload_user_image,null=True,blank=True)
    # UniqueCardNumber=models.BigIntegerField(null=False,unique=True,default=1700468209)

    # Add related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(
        Group,
        through=EmployeeGroup,
        through_fields=('employee', 'group'),
        related_name='employee_users',
        blank=True,
        verbose_name="groups",
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        through=EmployeePermission,
        through_fields=('employee', 'permission'),
        related_name='employee_users',
        blank=True,
        verbose_name="user permissions",
        help_text="Specific permissions for this user.",
        error_messages={
            'add': 'Error message 1',
            'remove': 'Error message 2',
        },
    )
    UniqueCardNumber=models.DateTimeField(null=False,default=datetime(2023, 1, 1, tzinfo=timezone.utc))
    cardNo= models.BigIntegerField(default=get_timestamp)
    department=models.ForeignKey("department.Department",on_delete=models.SET_NULL,null=True)
    designation=models.ForeignKey("designation.Designation",on_delete=models.SET_NULL,null=True)
    department_name = models.CharField(max_length=100, null=True, blank=True)
    designation_name = models.CharField(max_length=100, null=True, blank=True)
    shift_name = models.CharField(max_length=100, null=True, blank=True)
    group_name=models.CharField(max_length=100,null=False,default="-")

    def __str__(self):
        return self.employee_id
    def save(self, *args, **kwargs):
        # Fetch the corresponding Department and Designation instances
        if self.department_id:
            department_instance = Department.objects.get(pk=self.department_id)
            self.department_name = department_instance.department

        if self.designation_id:
            designation_instance = Designation.objects.get(pk=self.designation_id)
            self.designation_name = designation_instance.designation
        if self.shift_id_id:
            shift_instance = ShiftManagement.objects.get(pk=self.shift_id_id)
            self.shift_name = shift_instance.shift_name
        if self.group_id_id:
            print("group_id:", self.group_id_id)
            try:
                group_instance = Group.objects.get(pk=self.group_id_id)
                self.group_name = group_instance.group_name
            except ObjectDoesNotExist: pass
                # # Handle the case when the Group does not exist for the provided group_id_id
                # # For example, set a default value or handle the situation based on your logic
                # self.group_name = "-"  # Set a default group name or handle accordingly

        super().save(*args, **kwargs)





    
    USERNAME_FIELD='employee_id'
    REQUIRED_FIELDS=['password']

    def set_password(self, password):
        # Hash the raw password using make_password
        self.password = make_password(password)

    
    
class EmployeeGroupDevice(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(Employee,on_delete=models.CASCADE,null=False)
    device_id = models.ForeignKey(Devices,on_delete=models.CASCADE,null=False)
    action=models.CharField(max_length=100,null=False,default="-")
    job_start_date=models.DateTimeField(max_length=100,null=True,auto_now_add=True)




###train user from csv
    
def user_file_upload(filename):
    
    print("path : ","files/{filename}".format(filename=filename))
    return "files/{filename}".format(filename=filename)



class TrainEmployeeFromCSV(models.Model):
    file=models.FileField(upload_to=user_file_upload,null=False,blank=False)
    def __str__(self):
        return self.file
