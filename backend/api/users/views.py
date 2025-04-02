import logging
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import User
from .serializers import RegisterSerializer, UserSerializer
from .permissions import IsManager

logger = logging.getLogger("audit")


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: openapi.Response('User created')},
        operation_description="Register a new user. Default role is 'client'. Only managers can assign other roles."
    )
    def post(self, request):
        data = request.data.copy()
        if 'role' in data and data['role'] != 'client':
            if not request.user.is_authenticated or request.user.role != 'manager':
                raise PermissionDenied("Only managers can assign roles other than 'client'.")
        else:
            data['role'] = 'client'

        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"User registered: {user.username} with role {user.role}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Return details of the currently authenticated user.",
        responses={200: UserSerializer}
    )
    def get(self, request):
        user = request.user
        logger.info(f"User {user.username} fetched their profile.")
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        })


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsManager]

    @swagger_auto_schema(
        operation_description="Return a list of all users. Accessible to managers only.",
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"Manager {request.user.username} fetched user list.")
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsManager]

    @swagger_auto_schema(
        operation_description="Retrieve a user's details. Accessible to managers only.",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"Manager {request.user.username} fetched details for user ID {kwargs.get('pk')}")
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="Update a user's information. Accessible to managers only.",
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        logger.info(f"Manager {request.user.username} updated user ID {kwargs.get('pk')}")
        return super().patch(request, *args, **kwargs)
