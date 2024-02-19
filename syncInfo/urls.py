from django.urls import path
from .views import syncInfo,sync_info
urlpatterns=[
    path("",sync_info,name="syncinfo")
]