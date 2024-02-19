from django.db import models
from employee.models import Employee

class LogInLog(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="logins_employee_id")
    # username=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="logins_username")
    username=models.CharField(max_length=100,null=False,default="-")
    login_date=models.DateTimeField(null=True,auto_now_add=True)
    token=models.TextField(default="-",null=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['employee_id', 'username'], name='unique_employee_login')
    #     ]

