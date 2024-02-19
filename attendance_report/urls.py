from django.urls import path
from . import views

urlpatterns=[
    path('',views.attendanceReport,name="attendanceReport"),
    path('<int:pk>/',views.attendance_with_id,name="attendance_with_id"),
    path('<str:employee_id>',views.find_employee_data,name="find_employee_data"),
]
