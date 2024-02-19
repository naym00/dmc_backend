from django.urls import path
from . import views

urlpatterns=[
    path("",views.check_emp_group_device,name="check_emp_group_device"),
]