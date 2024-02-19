from django.urls import path
from . import views
urlpatterns=[
    path("",views.delete_previous_log_data,name="delete_previous_log_data"),
    
]