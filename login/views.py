# login/views.py

from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from devices.check_device_status import is_device_active
from devices.models import Devices
from devices.serializers import DevicesSerializer
from employee.models import Employee  # Import the Employee model
from employee.serializers import EmployeeSerializer  # Import the serializer for the Employee model
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import RefreshToken

import jwt
from django.contrib.auth.hashers import make_password, check_password
from .models import LogInLog


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = request.data
        employee_id = data.get('employee_id')
        password = data.get('password')
        print("employee_id :",employee_id,", password :",password)

        if employee_id and password:
            # for user in Employee.objects.all():
            #     user.password = make_password(user.password)
            #     user.save()
            hashed_password = make_password(password)

            user = authenticate(request,employee_id=employee_id, password=password)

            if user is not None:
                print("user.password :",user.password,", pasword : ",hashed_password)

                expiration_time = datetime.utcnow() + timedelta(hours=2)
                expiration_time_gmt6 = expiration_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=6)))

                exp_timestamp = int(expiration_time_gmt6.timestamp())

                # dev=Devices.objects.all().order_by('-device_id')
                # print("devices data :",dev)
                # devserializer=DevicesSerializer(dev,many=True)
                # dev_datas=devserializer.data
                # dev_status=[]
                # print("count : ",len(dev_datas))
                # for i in range(len(dev_datas)):
                #     if dev_datas[0]["device_ip"]==None:
                #         dev_status.append({"device_id":dev_datas[i]["device_id"],"device_ip":"null","active_status":dev_datas[i]["active_status"],"present_active_status": "inactive"})
                #         continue

                #     print(dev_datas[0]["device_id"])
                #     present_active_status= is_device_active(dev_datas[i]["device_ip"])
                #     present_active_status_str=""
                #     if present_active_status==True:
                #         present_active_status_str="active"
                #     else:
                #         present_active_status_str="inactive"
                    
                #     dev_status.append({"device_id":dev_datas[i]["device_id"],"device_ip":dev_datas[i]["device_ip"],"active_status":dev_datas[i]["active_status"],"present_active_status": present_active_status_str})
                # print("device_status",dev_status)


                body={
                    'id':employee_id,
                    'sub': "3346363",
                    'iat': int(datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=6))).timestamp()),
                    'exp': exp_timestamp,  # Add the expiration time
                    }
                emp=Employee.objects.get(employee_id=employee_id)
                print("user : ",emp)
                
                refresh = RefreshToken.for_user(emp)


                # token = jwt.encode(body, settings.SECRET_KEY, algorithm='HS256')
                # decoded_token = jwt.decode(token,settings.SECRET_KEY ,algorithms=['HS256'])
                # try:
                #     decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                #     print(decoded_token)
                # except jwt.ExpiredSignatureError:
                #     print("Token has expired")
                # except jwt.InvalidSignatureError as e:
                #     print("Signature verification failed")
                #     print(f"Encoded Signature: {e.signature}")
                #     print(f"Expected Signature: {e.expected_signature}")
                # # print(decoded_token)
                employee=Employee.objects.get(employee_id=employee_id)
                username=Employee.objects.filter(employee_id=employee_id).values_list("username",flat=True)
                final_token=str(refresh.access_token)
                
                log_insert=LogInLog(employee_id=employee,username=username,token=final_token)
                log_insert.save()
                

                serializer = EmployeeSerializer(user)
                return JsonResponse(
                        {
                        
                        'refresh':str(refresh),
                        'access':final_token,
                        'user': serializer.data,
                        }
                )
                # return Response({'token': token, 'user': serializer.data}, status=status.HTTP_200_OK)
            else:
                msg = 'Unable to log in with provided credentials.'
                return Response({'error': msg}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            msg = 'Must include "email" and "password".'
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)



# serializers.py
# from rest_framework import serializers

# class PasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()

# # views.py
# from django.contrib.auth.models import User
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# # from rest_framework_simplejwt.tokens import PasswordResetToken

# @api_view(['POST'])
# def forgot_password(request):
#     serializer = PasswordResetSerializer(data=request.data)
#     if serializer.is_valid():
#         email = serializer.validated_data['email']
#         user = User.objects.get(email=email)

#         if user:
#             # Generate a password reset token
#             token = PasswordResetToken.for_user(user)
            
#             # Send the reset link via email (you need to implement this part)
#             # email contains a link like: https://yourdomain.com/reset-password/?token=generated_token

#             return Response({'success': 'Password reset link sent successfully.'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # @api_view(['POST'])
# # def reset_password(request):
# #     token = request.data.get('token')
# #     new_password = request.data.get('new_password')

# #     if not token or not new_password:
# #         return Response({'error': 'Token and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)

# #     try:
# #         # Verify the password reset token
# #         payload = PasswordResetToken(token).payload
# #         user = User.objects.get(id=payload['user_id'])

# #         # Set the new password for the user
# #         user.set_password(new_password)
# #         user.save()

# #         return Response({'success': 'Password reset successfully.'}, status=status.HTTP_200_OK)
# #     except Exception as e:
# #         return Response({'error': 'Invalid token or user not found.'}, status=status.HTTP_400_BAD_REQUEST)
