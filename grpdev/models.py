from django.db import models
from empgrp.models import Group
from devices.models import Devices

# Create your models here.
class GroupDevice(models.Model):
    id = models.AutoField(primary_key=True)
    group_id =   models.ForeignKey(Group,on_delete=models.CASCADE,related_name="group_group_id")
    device_id =  models.ForeignKey(Devices,on_delete=models.CASCADE,null=False)
    group_name=models.CharField(max_length=100,null=False,default="-")
    device_name=models.CharField(max_length=100,null=False,default="-")

    def __str__(self):
        return self.id
    
    def save(self, *args, **kwargs):
        # Fetch the corresponding Department and Designation instances
        if self.group_id_id:
            group_instance = Group.objects.get(pk=self.group_id_id)
            self.group_name = group_instance.group_name

        if self.device_id_id:
            designation_instance = Devices.objects.get(pk=self.device_id_id)
            self.device_name = designation_instance.device_name

        super().save(*args, **kwargs)

