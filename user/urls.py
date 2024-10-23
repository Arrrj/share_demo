from django.contrib import admin
from django.urls import path

from user.api.v1.views.auth_views import Login, UserSignup, OtpVerification
from user.api.v1.views.profile_views import CompanyAPIView


urlpatterns = [
    path("signup/", UserSignup.as_view(), name="user_signup"),
    path("verify-otp/", OtpVerification.as_view(), name="verify_otp"),
    path("login/", Login.as_view(), name="login"),
    path("company-profile/", CompanyAPIView.as_view(), name="create-profile"),
]
