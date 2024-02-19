from datetime import datetime, time, timedelta
from django.db import models

from department.models import Department
from designation.models import Designation

# Create your models here.
class ShiftManagement(models.Model):
    shift_id=models.AutoField(primary_key=True)
    shift_beginning=models.TimeField(default="00:00:00")
    shift_end=models.TimeField(default="00:00:00")
    total_time=models.DurationField(blank=True, null=True)
    shift_name=models.CharField(max_length=100,null=True,default="-")
    def save(self, *args, **kwargs):
        # Ensure shift_beginning and shift_end are valid time objects
        if isinstance(self.shift_beginning, time) and isinstance(self.shift_end, time):
            # Calculate the time difference and update total_time before saving
            beginning = datetime.combine(datetime.min, self.shift_beginning)
            end = datetime.combine(datetime.min, self.shift_end)

            # Check if end time is earlier than the beginning (indicating a change in date)
            if end < beginning:
                end += timedelta(days=1)  # Increment by 1 day to represent the next day

            self.total_time = end - beginning

        super().save(*args, **kwargs)
    


class ShiftAssign(models.Model):
    employee_id=models.ForeignKey("employee.Employee",on_delete=models.CASCADE)
    employee_name=models.CharField(max_length=100,null=True,blank=True)
    shift_id=models.ForeignKey("shift_management.ShiftManagement",on_delete=models.CASCADE)
    shift_name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Fetch the corresponding Department and Designation instances
        if self.shift_id_id:
            shift_instance = ShiftManagement.objects.get(pk=self.shift_id_id)
            self.shift_name = shift_instance.shift_name
        if self.employee_id_id:
            employee_instance = self.employee_id
            self.employee_name = employee_instance.username   


        super().save(*args, **kwargs)
