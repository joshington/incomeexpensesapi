from logging import exception
from django.http import request
from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,\
    DjangoUnicodeDecodeError
#force_str ==> gives us a human readable id
from django.contrib.sites.shortcuts import get_current_site #gives current site we are on
from django.urls import reverse 
from .utils import Util

from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6,write_only=True)

    class Meta:
        model=User
        fields = ['email','username','password']

    def validate(self,attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        if not username.isalnum():
            raise serializers.ValidationError('The username should only contain alphanumeric xters')
        return attrs
        # return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token=serializers.CharField(max_length=555)
    

    class Meta:
        model=User
        fields=['token']

class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255,min_length=3)
    password=serializers.CharField(max_length=68,min_length=6,write_only=True)
    username=serializers.EmailField(max_length=255,min_length=3,read_only=True)
    tokens=serializers.CharField(max_length=68,min_length=6,read_only=True)



    class Meta:
        model = User
        fields = ['email','password','username','tokens']
    def validate(self,attrs):
        email=attrs.get('email', '')
        password=attrs.get('password','')

        user=auth.authenticate(email=email,password=password)
        #ucan use pdb to trace
        # import pdb
        # pdb.set_trace()
        #u can use it for your debugging cases
        if not user:
            raise AuthenticationFailed('Invalid credentials try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        
        return {
            'email':user.email,
            'username':user.username,
            'tokens':user.tokens,
        }
        return super().validate(attrs)

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email=serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']

    def validate(self,attrs):
        email = attrs['data'].get('email','')
            #have to filter whether email provided exists
            #then after filtering e have to get the user himself

            
                # return attrs
        return super().validate(attrs)

class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(
        min_length=6, max_length=68,write_only=True)
    token=serializers.CharField(
        min_length=1, max_length=6,write_only=True)
    uidb64=serializers.CharField(
        min_length=1,write_only=True)

    class Meta:
        fields = ['password','token','uidb64']

    def validate(self, attrs):
        try:
            password=attrs.get('password')
            token=attrs.get('token')
            uidb64 = attrs.get('uidb64')
            id=force_str(urlsafe_base64_decode(uidb64))#we use force_str to make sure its human
            #readable after decoding the id
            user=User.objects.get(id=id)

            #checking whether the token has not been used before
            if not PasswordResetTokenGenerator.check_token(user,token):
                raise AuthenticationFailed('The reset link is invalid',401)
            user.set_password(password)
            user.save()
            return user
            #after user has provided their password we need to set as their new password.
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid',401)
        return super().validate(attrs)