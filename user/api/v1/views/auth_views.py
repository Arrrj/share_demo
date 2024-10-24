from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime  
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.otp_utils import OtpUtils
from utils.email_utils import EmailUtils


from user.api.v1.serializers.auth_serializer import (
    EmailRegistrationSerializer,
    OtpVerificationSerializer,
    UserLoginSerializer,
    SetPasswordSerializer,
)
from user.models import User


class EmailRegistration(APIView):
    serializer_class = EmailRegistrationSerializer

    @swagger_auto_schema(
        operation_description="User registration",
        request_body=EmailRegistrationSerializer,
        responses={
            201: openapi.Response("User Registered Successfully"),
            400: openapi.Response(
                "Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            409: openapi.Response(
                "Conflict",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    
    def post(self, request):
        serializer = EmailRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "A user with this username already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            otp = OtpUtils.six_digit_otp()

            EmailUtils.otp_verification_mail(otp=otp, email=email)
        
            request.session['email'] = email
            request.session['otp'] = otp
            request.session['otp_created_at'] = timezone.now().isoformat()

            # print(request.session.__dict__)
            
            return Response(
                {"message": "Otp Send to user mail successfully"},
                status=status.HTTP_201_CREATED,
            )
      
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OtpVerification(APIView):
    serializer_class = OtpVerificationSerializer

    @swagger_auto_schema(
        operation_description="Verify OTP for email",
        request_body=OtpVerificationSerializer,
        responses={
            200: openapi.Response("OTP Verification Successful"),
            400: openapi.Response(
                "Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            404: openapi.Response(
                "User Not Found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Verify the OTP for the specified email.
        """
        serializer = OtpVerificationSerializer(data=request.data)

        if serializer.is_valid():

            email = request.session.get('email')
            otp = request.session.get('otp')
            otp_created_at_str = request.session.get('otp_created_at')

            if not email:
                return Response({"message": "Email not found in session"}, status=status.HTTP_404_NOT_FOUND)

            if not otp:
                return Response(
                    {"message": "Invalid OTP"}, status=status.HTTP_404_NOT_FOUND
                )
            
            otp_created_at = parse_datetime(otp_created_at_str)

            if otp_created_at is None:
                return Response({"message": "OTP creation time not found"}, status=status.HTTP_400_BAD_REQUEST)

            if timezone.is_naive(otp_created_at):
                otp_created_at = timezone.make_aware(otp_created_at)

            time_difference = timezone.now() - otp_created_at
            ten_minutes = timedelta(minutes=10)

            if time_difference > ten_minutes:
                return Response(
                    {"message": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST
                )
            if otp != serializer.validated_data.get('otp'):
                return Response(
                    {"message": "OTP does not match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": "OTP Verification Sussessful"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPassword(APIView):
    @swagger_auto_schema(
       operation_description="Set user password after email verification",
        request_body=SetPasswordSerializer,
        responses={
            200: openapi.Response(
                "Password set successfully.",
            ),
            400: openapi.Response(
                "Error in setting password.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message explaining what went wrong"),
                    }
                )
            )
        }
    )

    def post(self, request):
        email = request.session.get('email')

        if not email:
            return Response({'error': 'Email not found in session.'}, status=status.HTTP_400_BAD_REQUEST)
        

        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = User(email=email)
            password = serializer.validated_data['password']
            user.password = make_password(password)
            user.user_role = 'recruiter'
            user.save()

            request.session.flush()

            return Response({'message': 'Password set successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Login(APIView):
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        operation_description="User login",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                "Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                                "access": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
            401: openapi.Response(
                "Invalid Login Credentials",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            400: openapi.Response(
                "Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """
        View to handle user login.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(request=self.request, email=email, password=password)
            if not user:
                return Response(
                    {"message": "Invalid Login Credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            refresh = RefreshToken.for_user(user)
            response_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(
                {"message": "Success", "data": response_data}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
