from django.urls import path
from . import views

urlpatterns=[
    path('',views.group,name="group"),
    path('<int:pk>/',views.group_with_id,name="group_with_id"),
    path('assign-group/<int:groupid>/',views.assignGroup,name="assign-group"),
]