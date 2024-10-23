from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response


from user.api.v1.serializers.profile_serializer import CompanyProfileSerializer


class CompanyAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Create a company profile",
        request_body=CompanyProfileSerializer,
        responses={201: "Profile Created", 400: "Bad Request"},
    )
    def post(self, request):
        """
        View to handle company profile creation.
        """
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = CompanyProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"message": "Profile Created Successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
