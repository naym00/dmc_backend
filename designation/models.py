from django.db import models

# Create your models here.
class Designation(models.Model):
    id=models.AutoField(primary_key=True)
    designation=models.CharField(max_length=100,null=False)
    description=models.TextField(null=True,default="-")
    def __str__(self):
        return self.designation
    
