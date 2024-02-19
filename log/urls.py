from django.urls import path
from . import views
urlpatterns =[
    path("",views.log,name="log"),
    path("raw_log/",views.raw_log,name="raw_log"),
    path("<int:pk>",views.log_with_minutes,name="log_with_minutes")
]