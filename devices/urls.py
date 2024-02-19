from django.urls import path
from .views import devices,devices_with_id
urlpatterns=[
    path("",devices,name="devices"),
    path("<str:pk>/",devices_with_id,name="devices_with_id"),


]