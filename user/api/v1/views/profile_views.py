from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response


from user.api.v1.serializers.profile_serializer import CompanyProfileSerializer, CompanyProfileResponseSerializer
from user.models import CompanyProfile
from user.permissions import IsRecruiter


class CompanyAPIView(APIView):
    permission_classes = [IsRecruiter]

    @swagger_auto_schema(
        operation_description="Create a company profile",
        request_body=CompanyProfileSerializer,
        responses={201: "Profile Created", 400: "Bad Request"},
    )
    def post(self, request):
        """
        View to handle company profile creation.
        """
        if request.user.user_role != "recruiter":
            return Response(
                {"message": "Authentication required"},
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

    @swagger_auto_schema(
    operation_description="Get the authenticated user's company profile",
    responses={
        200: "Profile Updated Successfully",
        404: "Profile not found",
        401: "Authentication required",
        }
    )

    def get(self, request):

        if not request.user.is_authenticated:
            return Response(
                {"message": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            company_profile = CompanyProfile.objects.get(user=request.user)
            serializer = CompanyProfileResponseSerializer(company_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CompanyProfile.DoesNotExist:
            return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)


    @swagger_auto_schema(
        operation_description="Update the authenticated user's company profile",
        request_body=CompanyProfileResponseSerializer,
        responses={
            200: "Profile Updated Successfully",
            400: "Invalid data",
            404: "Profile not found",
            401: "Authentication required",
        }
    )

    def put(self, request):
        
        if not request.user.is_authenticated:
            return Response({"message": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            company_profile = CompanyProfile.objects.get(user=request.user)
        except CompanyProfile.DoesNotExist:
            return Response({"message": "profile not found"})
        
        serializer = CompanyProfileSerializer(company_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"message": "Profile Updated Successfully"}, status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)