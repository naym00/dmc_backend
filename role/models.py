from django.db import models


# Create your models here.
class Role(models.Model):
    role_id=models.AutoField(primary_key=True)
    role =models.CharField(max_length=100,null=False, unique=True)
    role_description=models.CharField(max_length=200,null=True,default="-")


    def __str__(self):
        return self.role
    

