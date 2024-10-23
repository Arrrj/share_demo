from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.otp_utils import OtpUtils
from utils.email_utils import EmailUtils


from user.api.v1.serializers.auth_serializer import (
    UserSignupSerializer,
    EmailVerifySerializer,
    UserLoginSerializer,
)
from user.models import User


class UserSignup(APIView):
    serializer_class = UserSignupSerializer

    @swagger_auto_schema(
        operation_description="User registration",
        request_body=UserSignupSerializer,
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
        """
        Create a new user.
        """

        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            password = make_password(serializer.validated_data["password"])
            email = serializer.validated_data["email"]
            user_role = serializer.validated_data["user_role"]

            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "A user with this username already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_obj, created = User.objects.get_or_create(
                email=email, password=password
            )
            if created:
                otp = OtpUtils.six_digit_otp()
                user_obj.otp = otp
                user_obj.user_role = user_role
                user_obj.otp_created_at = timezone.now()
                user_obj.save()

                EmailUtils.otp_verification_mail(otp=otp, email=email)

                return Response(
                    {"message": "User Registered Successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": "User ALready Exist"}, status=status.HTTP_409_CONFLICT
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OtpVerification(APIView):
    serializer_class = EmailVerifySerializer

    @swagger_auto_schema(
        operation_description="Verify OTP for email",
        request_body=EmailVerifySerializer,
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
        serializer = EmailVerifySerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]

            user_obj = User.objects.filter(email=email).first()

            if not user_obj:
                return Response(
                    {"message": "Invalid OTP"}, status=status.HTTP_404_NOT_FOUND
                )
            time_difference = timezone.now() - user_obj.otp_created_at
            ten_minutes = timedelta(minutes=10)

            if time_difference > ten_minutes:
                return Response(
                    {"message": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST
                )
            if user_obj.otp != otp:
                return Response(
                    {"message": "OTP does not match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_obj.email_verification = True
            user_obj.save()
            return Response(
                {"message": "OTP Verification Sussessful"}, status=status.HTTP_200_OK
            )
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
