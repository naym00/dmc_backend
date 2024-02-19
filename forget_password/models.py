from django.db import models
from employee.models import Employee
# Create your models here.
class ForgetPassword(models.Model):
    ID=models.AutoField(primary_key=True)
    employee_id=models.ForeignKey("employee.Employee",on_delete=models.CASCADE)
    email=models.EmailField(default="example@gmail.com",null=False)
    token=models.TextField()
    creation_date=models.DateTimeField(null=False)
    expiration_date=models.DateTimeField(null=False)
    