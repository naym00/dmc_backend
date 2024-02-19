from django.urls import path
from . import views
urlpatterns=[
    path('',views.role,name="role"),
    path('<int:pk>/',views.role_with_id,name="role_with_id"),
    
]