from django.urls import path
from . import views

urlpatterns=[
    path("",views.department,name="department"),
    path("<int:pk>/",views.department_with_id,name="department_with_id")
]
