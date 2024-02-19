from django.urls import path
from . import views

urlpatterns=[
    path('',views.designation,name="designation"),
    path('<int:pk>/',views.designation_with_id,name="designation_with_id"),
]
