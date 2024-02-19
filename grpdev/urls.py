from django.urls import path
from . import views

urlpatterns=[
    path('',views.empgrpdev,name="empgrpdev"),
    path('<int:pk>/',views.empgrpdev_with_id,name="empgrpdev_with_id")
]