from mysqlx import IntegrityError
from .serializers import RoleSerializer
from .models import Role
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['GET','POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def role(request):
    if request.method == 'GET':
        role_data=Role.objects.all().order_by('-role_id')
        role_serializer = RoleSerializer(role_data,many=True)
        return Response(role_serializer.data)
    if request.method == 'POST':
        role_serializer = RoleSerializer(data=request.data)
        try:
            if role_serializer.is_valid():
                role_serializer.save()
                return Response(role_serializer.data)
        except IntegrityError:
            return Response({'error': 'Role name must be unique.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(role_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return

@api_view(['GET','POST','DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def role_with_id(request,pk):
    check=Role.objects.filter(role_id=pk).exists()

    print("check :",check)
    if check:
        # find=Role.objects.filter(role_id=pk).first()
        role_data = Role.objects.get(role_id=pk)
        
        if request.method == 'GET':
            role_serializer = RoleSerializer(role_data)
            return  Response(role_serializer.data)
        if request.method == 'POST' :
            role_serializer = RoleSerializer(instance = role_data,data=request.data)
            if role_serializer.is_valid():
                role_serializer.save()
                return  Response(role_serializer.data)
            else:
                return Response(role_serializer.error,status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            role_data.delete()
            return Response({"message":"Role Successfully deleted !"})

    else:
        return Response({"message":"Role Not Exist!"})



    
    