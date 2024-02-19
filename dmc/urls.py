
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('employee/', include('employee.urls')),
    path('department/',include('department.urls')),
    path('designation/',include('designation.urls')),
    path('devices/',include('devices.urls')),

    path('empgrp/',include('empgrp.urls')),
    path('role/',include('role.urls')),
    path('empfiles/',include('empfiles.urls')),
    path('grpdev/',include('grpdev.urls')),
    path('login/',include('login.urls')),
    path('log/',include('log.urls')),
    path('forget_password/',include('forget_password.urls')),
    path('attendance_log/',include('attendance_report.urls')),
    path('sync_info/',include('syncInfo.urls')),
    path('shift/',include('shift_management.urls')),
    path('status/',include('device_status.urls')),
    path('structuedlog/',include('structuedlog.urls')),
    path('archive_log/',include('archive_log.urls')),
    path('employee_csv/',include('employee_csv.urls')),
    path('shift_assign/',include('shift_assign.urls')),
    path('dashboard/',include('dashboard.urls')),
    path('security/',include('security.urls')),
    path('employee_list_add/',include('employee_list_add.urls')),
    
    

    
    

    

    

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)