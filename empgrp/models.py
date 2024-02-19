from django.db import models

# Create your models here.
class Group(models.Model):
    group_id=models.AutoField(primary_key=True)
    group_name=models.CharField(max_length=100,null=False)
    Remaks = models.CharField(max_length=100,null=True,default="-")
