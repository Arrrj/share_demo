from django.contrib import admin
from django.urls import path

from user.api.v1.views.auth_views import Login, EmailRegistration, SetPassword, OtpVerification
from user.api.v1.views.profile_views import CompanyAPIView


urlpatterns = [
    path("email-register/", EmailRegistration.as_view(), name="email_register"),
    path("verify-otp/", OtpVerification.as_view(), name="verify_otp"),
    path("set-password/", SetPassword.as_view(), name="set_password"),
    path("login/", Login.as_view(), name="login"),
    path("company-profile/", CompanyAPIView.as_view(), name="create-profile"),
]
