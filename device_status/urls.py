from django.urls import path
from .views import devices_status,devices_status_with_id
urlpatterns=[
    path("",devices_status,name="devices_status"),
    path("<str:pk>/",devices_status_with_id,name="devices_status_with_id")

]