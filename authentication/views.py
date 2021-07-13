from django.core.mail import message
from django.shortcuts import render
from rest_framework import generics, status,views
from rest_framework import serializers
from rest_framework.serializers import Serializer
from .serializers import*
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.
from .models import User
from .utils import*
from django.contrib.sites.shortcuts import get_current_site
#since we need the user to click on the link and the link should be able to bring the user
#back to our application
from django.urls import reverse  #reverse takes in aurl name and give us the path
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import*
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,\
    DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site #gives current site we are on
from django.urls import reverse 
from .utils import Util




class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)
    def post(self,request):
        user = request.data 
        serializer=self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data=serializer.data
        user=User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token#mthd  to get accesstoken

        #since we have to send alink so we will need this to get the site
        current_site=get_current_site(request).domain
        relativeLink=reverse('email-verify')#page that they go to when they click on the link
        #we use reverse since we need the path to the verify email link
        #reverse takes in the url name and then gives us the path
        
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        #   'domain':absurl,
        email_body = 'Hi '+user.username+'/tUse link below to verify your email \n'+absurl
        data={
            'email_body':email_body,
            'to_email':user.email,
            'email_subject':'Verify your email'
        }
        Util.send_email(data)
        return Response(user_data,status=status.HTTP_201_CREATED)


#class to verify the email
class VerifyEmail(views.APIView):
    serializer_class=EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token',in_=openapi.IN_QUERY,
        description='Description',type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request):
        token = request.GET.get('token')
        #above gets us token being sent to the user
        try:
            payload = jwt.decode(token,  settings.SECRET_KEY)
            user=User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified=True
                user.save()
            #we have decoded to get the user then set that the user is verified
            return Response(
                {'email':'Successfully activated'},
                status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error':'Activation Link EXpired'},
                status=status.HTTP_400_BAD_REQUEST
            )
            #our except handles case where the token has expired
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error':'Invalid token'},status=status.HTTP_400_BAD_REQUEST)
            #this exception is when the user has messes up with the token.

class LoginAPIView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True) 

        return Response(serializer.data,status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer 

    def post(self, request):
        # data = {'request':request,'data':request.data}
        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        email=request.data['email']
        if User.objects.filter(email=email).exists():
                user=User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token=PasswordResetTokenGenerator().make_token(user)

                current_site=get_current_site(request=request).domain
                relativeLink=reverse('password-reset-confirm',
                    kwargs={'uidb64':uidb64,'token':token})#page that they go to when they click on the link
                #we use reverse since we need the path to the verify email link
                #reverse takes in the url name and then gives us the path
                
                absurl = 'http://'+current_site+relativeLink
                #   'domain':absurl,
                email_body = 'Hello, \n Use link below to reset  your password \n'+absurl
                data={
                    'email_body':email_body,
                    'to_email':user.email,
                    'email_subject':'Reset your password'
                }
                Util.send_email(data)
        return Response(
            {'success':'We have sent you alink to reset your password'},
            status=status.HTTP_200_OK
        )


class PasswordTokenCheckAPIView(generics.GenericAPIView):
    def get(self,request,uidb64,token):
        try:
            id=smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=id)
            #check if the token is not already in use
            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response(
                    {
                        'error':'Token is not valid,please request a new one'
                    },status=status.HTTP_401_UNAUTHORIZED
                )
            return Response({'success':True,'message':'Credentials are valid',
                'uidb64':uidb64,'token':token
            },status=status.HTTP_200_OK)
            #use smart_str since user has to open the token in the link
            
        #incase our token is being tampered by the user
        except DjangoUnicodeDecodeError as identifier:
            return Response(
                {'error':'Token is not valid,please request a new one'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                'success':True,
                'message':'Password reset success'
            },
            status=status.HTTP_201_CREATED
        )