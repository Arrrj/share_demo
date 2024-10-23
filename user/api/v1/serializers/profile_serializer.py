from rest_framework import serializers

from user.models import CompanyProfile


class CompanyProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField()
    
    class Meta:
        model = CompanyProfile
        fields = '__all__'