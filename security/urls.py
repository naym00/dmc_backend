from django.urls import path
from . import  views

urlpatterns=[
    path("<str:pk>/",views.security_info,name="security_info")
]