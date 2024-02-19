from django.urls import path
from . import views
urlpatterns=[
    path("",views.structured_log,name="structured_log")
]