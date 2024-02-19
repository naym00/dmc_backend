from django.urls import path
from . import views
urlpatterns=[
    path("",views.assign_shift,name="assign_shift"),
    path("<int:pk>/",views.assign_shift_with_id,name="assign_shift_with_id"),
    path("bulk/<int:shiftid>/",views.assign_shift_bulk,name="assign-shift-bulk")
]