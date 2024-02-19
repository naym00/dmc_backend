from django.db import models

def user_file_upload(instance,filename):
    
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png") or filename.endswith(".JPG") or filename.endswith(".JPEG") or filename.endswith(".PNG"):
        print("path : ","{employee_id}/images/{filename}".format(employee_id=instance.employee_id,filename=filename))
        return "{employee_id}/images/{filename}".format(employee_id=instance.employee_id,filename=filename)
    else:
        print("path : ","{employee_id}/files/{filename}".format(employee_id=instance.employee_id,filename=filename))
        return "{employee_id}/files/{filename}".format(employee_id=instance.employee_id,filename=filename)



class EmployeeFiles(models.Model):
    employee_id = models.ForeignKey("employee.Employee",on_delete=models.CASCADE,null=True)
    file=models.FileField(upload_to=user_file_upload,null=False,blank=False)
    file_description = models.CharField(max_length=200,null=True,default="-")
    def __str__(self):
        return self.file
