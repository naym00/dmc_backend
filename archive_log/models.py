from django.db import models
from datetime import datetime,timedelta


# Create your models here.
def check_time():
    archive_time=datetime.now()+timedelta(hours=6)
    return  archive_time


class Archivelog(models.Model):
    id = models.AutoField(primary_key=True)
    archive_time=models.DateTimeField(max_length=100,null=False,default=check_time)
    employee_id=models.ForeignKey("employee.Employee",on_delete=models.CASCADE)


