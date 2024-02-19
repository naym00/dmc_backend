from django.shortcuts import render

# Create your views here.
# myapp/auth.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta

class CustomJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        """
        Override the get_validated_token method to set the access token lifetime.
        """
        print("updating lifetime of accees token")
        validated_token = super().get_validated_token(raw_token)
        validated_token_1=validated_token

        # Set the desired access token lifetime (e.g., 1 hour)
        access_token_lifetime = timedelta(hours=1)
        validated_token.payload['exp'] = validated_token.current_time + access_token_lifetime.total_seconds()
        if validated_token_1==validated_token:
            print("both tokens are same")

        return validated_token
