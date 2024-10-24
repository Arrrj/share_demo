from rest_framework import serializers

from user.models import CompanyProfile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class CompanyProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CompanyProfile
        fields = '__all__'

class CompanyProfileResponseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = CompanyProfile
        fields = ['name','user','company_name','company_mail','contact_number']