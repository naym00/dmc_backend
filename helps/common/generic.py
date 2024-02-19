from devices.check_device_status import is_device_active
from requests.auth import HTTPDigestAuth
from datetime import datetime
from PIL import Image
import requests
import base64
import os
import re

class Generichelps:
    
    def getDeviceIpUsernamePassword(self, Classobject, deviceid):
        ip = '0.0.0.0'
        username = 'admin'
        password = 'admin'
        activity = 'inactive'
        objects = Classobject.objects.filter(device_id=deviceid)
        if objects.exists():
            object = objects.values("device_ip", "username", "password", "active_status").first()
            ip = object.get('device_ip', '0.0.0.0')
            username = object.get('username', 'admin')
            password = object.get('password', 'admin')
            activity = object.get('active_status', 'admin')

        return ip, username, password, activity
    
    def checkExistence(self, Classobject, kwargs={}):
        return Classobject.objects.filter(**kwargs).exists()
    
    def validatejpgimg(self, strimg):
        flag = False
        if '.jpg' in strimg[len(strimg)-4:]: flag = True
        return flag
    
    def resize_image(self, input_path, output_path, max_size_kb):
        try:
            with Image.open(input_path) as img:
                original_size = os.path.getsize(input_path)
                original_width, original_height = img.size
                target_size_bytes = max_size_kb * 1024
                scale_factor = 1.0
                if original_size > target_size_bytes:
                    scale_factor = (target_size_bytes / original_size) ** 0.5

                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                resized_img.thumbnail((230, 230)) 
                resized_img.save(output_path, optimize=True, quality=100)
        except MemoryError as e: pass

    def convertImgTobase64(self, image):
        img=image.read()
        base64_img=base64.b64encode(img)
        return base64_img.decode("utf-8")
    
    def getPhotoData(self, image_paths):
        PhotoData = []
        for image_path in image_paths:
            self.resize_image(image_path,image_path,80)
            with open(image_path,"rb") as image:
                PhotoData.append(self.convertImgTobase64(image))
        return PhotoData
    
    def get_record_number(self, deviceip, employee_id, deviceusername, devicepassword):
        url=f"http://{deviceip}/cgi-bin/recordFinder.cgi?action=find&name=AccessControlCard&condition.UserID={employee_id}&count={8000}"
        resp=requests.get(url, auth=HTTPDigestAuth(deviceusername, devicepassword))
        
        records = []

        # Split the text into lines
        lines = resp.text.split('\n')

        # Remove empty lines
        lines = [line for line in lines if line.strip()]

        current_index = None
        current_record = {}

        for line in lines:
            # Extract the index, field, and value using regular expressions
            match = re.match(r'records\[(\d+)\]\.(.*?)=(.*)', line)
            if match:
                index = int(match.group(1))
                field_name = match.group(2)
                value = match.group(3)

                if index != current_index:
                    if current_record:
                        records.append(current_record)
                    current_index = index
                    current_record = {}

                current_record[field_name] = value

        if current_record:
            records.append(current_record)
        return records[0]["RecNo"]
    
    def existanceofuser(self, deviceip, employee_id, deviceusername, devicepassword):
        flag = False
        try:
            url=f"http://{deviceip}/cgi-bin/recordFinder.cgi?action=find&name=AccessControlCard&condition.UserID={employee_id}&count={8000}"
            resp=requests.get(url, auth=HTTPDigestAuth(deviceusername, devicepassword))
            r=resp.text
            r=r.replace("found=","")
            flag = True if re.search('found=0', resp.text) == None else False
        except: flag = False
        return flag
    
    def insertusrwithoutimg(self, deviceip, username, cardno, employee_id, password, reg_date,  valid_date, deviceusername, devicepassword):
        flag = False
        url = f'http://{deviceip}/cgi-bin/recordUpdater.cgi?action=insert&name=AccessControlCard&CardName={username}&CardNo={cardno}&UserID={employee_id}&CardStatus=0&CardType=0&Password={password}&Doors[{0}]=0&VTOPosition=01018001&ValidDateStart={reg_date}%20093811&ValidDateEnd={valid_date}%20093811'
        response = requests.get(url, auth=HTTPDigestAuth(deviceusername, devicepassword))
        if response.status_code>=200 and response.status_code<299: flag = True
        return flag

    def addphototouser(self, image_paths, deviceip, employee_id, username, deviceusername, devicepassword):
        flag = False
        if self.existanceofuser(deviceip, employee_id, deviceusername, devicepassword):
            url=f"http://{deviceip}/cgi-bin/FaceInfoManager.cgi?action=add"
            data={
                "UserID": str(employee_id),
                "Info":{
                    "UserName":username,
                    "PhotoData": self.getPhotoData(image_paths)
                }
            }
            response = requests.post(url, json=data, auth=HTTPDigestAuth(deviceusername, devicepassword), headers={"Content-Type":"application/json"})
            print(response.status_code)
            if response.status_code>=200 and response.status_code<=299: flag = True
        return flag
    
    def deleteusr(self, deviceip, employee_id, deviceusername, devicepassword):
        flag = False
        RecordNumberFrom_Find_Employee_Info=int(self.get_record_number(deviceip, employee_id, deviceusername, devicepassword))
        url=f"http://{deviceip}/cgi-bin/recordUpdater.cgi?action=remove&name=AccessControlCard&recno={RecordNumberFrom_Find_Employee_Info}"
        response = requests.get(url,auth=HTTPDigestAuth(deviceusername, devicepassword))
        if response.status_code>=200 and response.status_code<299: flag = True
        return flag
    
    def deleteusrallimg(self, deviceip, employee_id, deviceusername, devicepassword):
        flag = False
        if self.existanceofuser(deviceip, employee_id, deviceusername, devicepassword):
            url = f'http://{deviceip}/cgi-bin/FaceInfoManager.cgi?action=remove&UserID={employee_id}'
            response = requests.get(url,auth=HTTPDigestAuth('admin', 'admin333'))
            if response.status_code>=200 and response.status_code<299: flag = True
        return flag

    def change_group_image(self, GroupDevice, Devices, previousgroupid, newgroupid, employee_details):
        if previousgroupid != newgroupid:
            newdevice_flag = False
            newdevices= GroupDevice.objects.filter(group_id=newgroupid).values_list('device_id', flat=True)
            for newdevice in newdevices:
                deviceip, deviceusername, devicepassword, deviceactivity = self.getDeviceIpUsernamePassword(Devices, newdevice)
                if deviceactivity=="active" and is_device_active(deviceip):
                    newdevice_flag = True

            if newdevice_flag:
                username = employee_details.username
                cardNo = employee_details.cardNo
                employee_id = employee_details.employee_id
                password = employee_details.password
                reg_date = f'{employee_details.registration_date}'.replace('-', '')
                valid_date = employee_details.validity_date.replace('-', '')

                devices= GroupDevice.objects.filter(group_id=previousgroupid).values_list('device_id', flat=True)
                for device in devices:
                    deviceip, deviceusername, devicepassword, deviceactivity = self.getDeviceIpUsernamePassword(Devices, device)
                    if deviceactivity=="active" and is_device_active(deviceip):
                        if self.existanceofuser(deviceip, employee_id, deviceusername, devicepassword):
                            self.deleteusr(deviceip, employee_id, deviceusername, devicepassword)

                for newdevice in newdevices:
                    deviceip, deviceusername, devicepassword, deviceactivity = self.getDeviceIpUsernamePassword(Devices, newdevice)
                    if deviceactivity=="active" and is_device_active(deviceip):

                        if self.insertusrwithoutimg(deviceip, username, cardNo, employee_id, password, reg_date, valid_date, deviceusername, devicepassword):
                            if employee_details.image:
                                if os.path.exists(employee_details.image.path):
                                    image_paths = [employee_details.image.path]
                                    flag = self.addphototouser(image_paths, deviceip, employee_id, username, deviceusername, devicepassword)
                                    print('Changed Group')
        else:
            username = employee_details.username
            employee_id = employee_details.employee_id
            devices= GroupDevice.objects.filter(group_id=newgroupid).values_list('device_id', flat=True)

            for device in devices:
                deviceip, deviceusername, devicepassword, deviceactivity = self.getDeviceIpUsernamePassword(Devices, device)
                if deviceactivity=="active" and is_device_active(deviceip):
                    if self.existanceofuser(deviceip, employee_id, deviceusername, devicepassword):
                        if self.deleteusrallimg(deviceip, employee_id, deviceusername, devicepassword):
                            if employee_details.image:
                                if os.path.exists(employee_details.image.path):
                                    image_paths = [employee_details.image.path]
                                    flag = self.addphototouser(image_paths, deviceip, employee_id, username, deviceusername, devicepassword)
                                    print('Changed Image')


    def bulkAssignGroup(self, Employee, GroupDevice, Devices, groupid, employeelist):
        message = {}
        devices= GroupDevice.objects.filter(group_id=groupid).values_list('device_id', flat=True)
        for device in devices:
            deviceip, deviceusername, devicepassword, deviceactivity = self.getDeviceIpUsernamePassword(Devices, device)
            if deviceactivity=="active" and is_device_active(deviceip):
                message.update({f'{deviceip}': {}})
                for employee_id in employeelist:
                    employee = Employee.objects.filter(employee_id=employee_id)
                    if employee.exists():
                        username = employee[0].username
                        cardNo = employee[0].cardNo
                        employee_id = employee[0].employee_id
                        password = employee[0].password
                        reg_date = f'{employee[0].registration_date}'.replace('-', '')
                        valid_date = employee[0].validity_date.replace('-', '')
                        if not self.existanceofuser(deviceip, employee_id, deviceusername, devicepassword):
                            if self.insertusrwithoutimg(deviceip, username, cardNo, employee_id, password, reg_date, valid_date, deviceusername, devicepassword):
                                if employee[0].image:
                                    if os.path.exists(employee[0].image.path):
                                        image_paths = [employee[0].image.path]
                                        flag = self.addphototouser(image_paths, deviceip, employee_id, username, deviceusername, devicepassword)
                                        if flag:
                                            message[f'{deviceip}'].update({employee_id: 'created!'})
                                        else:
                                            message[f'{deviceip}'].update({employee_id: 'image couldn\'t add!'})
                            else:
                                message[f'{deviceip}'].update({employee_id: 'not created!'})
                        else:
                            message[f'{deviceip}'].update({employee_id: 'already exists in access control device!'})
                    else:
                        message[f'{deviceip}'].update({employee_id: 'not exists in dmc db!'})
                        print('Employee doesn\'t Exist!')
            else:
                message.update({f'{deviceip}': {
                    'deviceactivity': deviceactivity,
                    'is_device_active': is_device_active(deviceip)
                }})
        return message   
