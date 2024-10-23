from rest_framework import serializers

from user.models import User


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'user_role',
            'password',
        ]


class EmailVerifySerializer(serializers.Serializer):
    email = serializers.CharField()
    otp = serializers.CharField()
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
