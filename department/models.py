from django.db import models

# Create your models here.
class Department(models.Model):
    id=models.AutoField(primary_key=True)
    department=models.CharField(max_length=100,null=False,default="-")
    description =models.TextField(null=True,default="-")
    def __str__(self):
        return self.department



