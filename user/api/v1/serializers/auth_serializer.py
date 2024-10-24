from rest_framework import serializers

from user.models import User


class EmailRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()



class OtpVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField()

class SetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
