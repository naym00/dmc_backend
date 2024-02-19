from django.urls import path
from . import views

urlpatterns=[
    path("",views.email_sending,name="email_sending"),
    path("<str:token>/",views.change_password,name="change_password"),
    
]