from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmployeeIdBackend(ModelBackend):
    def authenticate(self, request, employee_id=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(employee_id=employee_id)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
