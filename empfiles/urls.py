from .serializers import EmploeeFileSerializer
from django.urls import path
from . import views

urlpatterns=[
    path('',views.employeeFiles,name="employeeFiles"),
    path('<int:pk>/',views.employeeFiles_with_id,name="employeeFiles_with_id"),
]