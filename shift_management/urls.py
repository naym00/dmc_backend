from django.urls import path
from .views import shiftManagement,ShiftManagement_with_id
urlpatterns=[
    path("",shiftManagement,name="shift"),
    path("<int:pk>/",ShiftManagement_with_id,name="shift_with_id")
]