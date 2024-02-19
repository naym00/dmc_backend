from django.urls import path
from . import views
urlpatterns=[
    path("",views.dashboard_info,name="dashboard_info"),
]