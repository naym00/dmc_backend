# myapp/models.py
from django.db import models

class UploadedFile(models.Model):
    csv_file = models.FileField(upload_to='uploads/csv/',null=False)
    zip_file = models.FileField(upload_to='uploads/zip/',null=False)
