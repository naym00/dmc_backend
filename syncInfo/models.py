# models.py
from django.db import models
from django.utils import timezone

class SyncInfoTable(models.Model):
    id = models.AutoField(primary_key=True)
    syncTime = models.DateTimeField()
    employee_id = models.CharField(max_length=100, default="SYSTEM")
