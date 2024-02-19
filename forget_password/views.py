import os
import base64
from datetime import datetime, timedelta
import secrets
from django.forms import ValidationError
import pytz
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ForgetPassword
from employee.models import Employee
from .serializers import ForgetPasswordSerializer
from employee.serializers import EmployeeSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from dotenv import load_dotenv
load_dotenv()

@api_view(['POST'])
def email_sending(request):
    if 'email' in request.data:
        print("email :",request.data["email"])
        find=Employee.objects.filter(email=request.data["email"]).first()
        if find !=None:
            employee=Employee.objects.filter(email=request.data["email"]).first()
            random_string_1 = secrets.token_hex(3)
            random_string_2 = secrets.token_hex(3)
            random_string_3 = secrets.token_hex(3)
            random_string_4 = secrets.token_hex(3)
            serializer=EmployeeSerializer(employee)
            # Combine the user information JSON and the random string
            combined_data = random_string_1+"###"+ str(serializer.data['employee_id'])+str(serializer.data['password'])+random_string_4+str(serializer.data['cardNo'])+random_string_2+str(serializer.data['email'])+"###"+ random_string_3
            
            # Encode the combined data as bytes and then encode it to base64
            base64_encoded_combined_data = base64.b64encode(combined_data.encode()).decode()
            
            # Print the random base64-encoded combined data
            # print("Random Base64-encoded Combined Data:", base64_encoded_combined_data)
            sendmail(request.data["email"],base64_encoded_combined_data)
            dtime = datetime.now()

            # Convert to a Unix timestamp
            timestamp = dtime.timestamp()
            # Convert back to a datetime object
            utc_datetime = datetime.utcfromtimestamp(timestamp)
            # Convert to the desired timezone (Asia/Dhaka)
            desired_timezone = pytz.timezone('Asia/Dhaka')
            creation_dat = utc_datetime.astimezone(desired_timezone)
            print("creation date:", creation_dat)

            dt = datetime.now()+ timedelta(minutes=5)

            # Convert to a Unix timestamp
            tmp = dt.timestamp()
            # Convert back to a datetime object
            utc_dat = datetime.utcfromtimestamp(tmp)
            # Convert to the desired timezone (Asia/Dhaka)
            desired_tz = pytz.timezone('Asia/Dhaka')
            expire_dt = utc_dat.astimezone(desired_tz)
            print("exp date:", expire_dt)



            data=ForgetPassword(
                employee_id=employee,
                email=request.data["email"],
                token=base64_encoded_combined_data,
                creation_date=creation_dat,
                expiration_date=expire_dt,
            )
            data.save()
            return Response({"message":"email sent","data":base64_encoded_combined_data})
        else:
            return Response({"message":"email not varified"})
    elif 'password' in request.data:
        password=request.data['password']
        print("password :",password)
        if 'Reset-Token' in request.headers:
            print("headers :",request.headers)
            token=request.headers['Reset-Token']
            print("token found :",token)
            exist=ForgetPassword.objects.filter(token=token).first()
            if exist!=None :
                print("exist :",exist)
                delel_data=ForgetPassword.objects.filter(token=token).first()
                if delel_data!=None:
                    expire_date=ForgetPassword.objects.filter(token=token).values_list("expiration_date","employee_id",flat=False)
                    print("employee id :",expire_date[0][1])
                    delele_data=ForgetPassword.objects.filter(employee_id=expire_date[0][1])
                    dt = datetime.now()
                    tmp = dt.timestamp()
                    utc_dat = datetime.utcfromtimestamp(tmp)
                    desired_tz = pytz.timezone('Asia/Dhaka')
                    curr_dt = utc_dat.astimezone(desired_tz)
                    if curr_dt>expire_date[0][0]:
                        print("curr_dt : ",curr_dt,"\nexpire_date",expire_date[0][0].replace(tzinfo=timezone.utc))
                        delele_data.delete()

                        return Response({"message": "Token expired"})
                    else:
                        print("curr_dt : ",curr_dt,"\nexpire_date",expire_date[0][0].replace(tzinfo=timezone.utc))
                        try:

                            emp=Employee.objects.get(employee_id=expire_date[0][1])
                            passw=request.data["password"]
                            hashed=make_password(passw)
                            request.data["password"]=hashed

                            empserializer=EmployeeSerializer(instance=emp,data= request.data, partial=True)
                            # print("empserializer data : ",empserializer.data)
                            if empserializer.is_valid():
                                # empserializer.data['password']=password
                                empserializer.save()
                                print("data",empserializer.data)
                                return Response({"message": "Password Changed successfully !!!","data":empserializer.data})
                        except Employee.DoesNotExist:
                            # Handle the case where no Employee with the given employee_id is found
                            print("Employee not found.")
                        except ValidationError as e:
                            # Handle validation errors if any occur
                            print("Validation error:", e)      
                            
                        return Response({"message": "Password Changed unsuccessfully !!!","data":empserializer.data})
                else:
                        print("exist :",delel_data)
                        return Response({"message": "Token is not valid"})
            else:
                print("exist :",exist)
                return Response({"message": "Token is not valid"})




            # return Response({"token": request.headers['Token']})


    else:
        return Response({"message":"Field should contain email only"})
    return
@api_view(['POST'])
def change_password(request,token):

    return
def createTime():
    # Get the current time and add 5 minutes
    dtime = datetime.now()

    # Convert to a Unix timestamp
    timestamp = dtime.timestamp()

    # Convert back to a datetime object
    utc_datetime = datetime.utcfromtimestamp(timestamp)

    # Associate with UTC timezone
    utc_timezone = pytz.timezone('UTC')
    utc_datetime = utc_timezone.localize(utc_datetime)

    # Convert to the desired timezone (Asia/Dhaka)
    desired_timezone = pytz.timezone('Asia/Dhaka')
    creation_date = utc_datetime.astimezone(desired_timezone)

    print("Expiration date:", creation_date)
    return creation_date.replace(tzinfo=timezone.utc),
def expireTime():
    # Get the current time and add 5 minutes
    dtime = datetime.now() + timedelta(minutes=5)

    # Convert to a Unix timestamp
    timestamp = dtime.timestamp()

    # Convert back to a datetime object
    utc_datetime = datetime.utcfromtimestamp(timestamp)

    # Associate with UTC timezone
    utc_timezone = pytz.timezone('UTC')
    utc_datetime = utc_timezone.localize(utc_datetime)

    # Convert to the desired timezone (Asia/Dhaka)
    desired_timezone = pytz.timezone('Asia/Dhaka')
    exp_date = utc_datetime.astimezone(desired_timezone)

    print("Expiration date:", exp_date)
    return exp_date.replace(tzinfo=timezone.utc),
    
def sendmail(email,token):
    subject="DMC login password change"
    email_from = settings.EMAIL_HOST_USER
    message=f"please got to {os.getenv('HTTP_HOST')}/auth/forgot-password?token={token}"
    send_mail(subject, message, email_from,[email,])
    return Response({"message":"mail sent"})