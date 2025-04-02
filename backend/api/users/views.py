from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import User
from .serializers import RegisterSerializer, UserSerializer
from .permissions import IsManager


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: openapi.Response('Utworzono użytkownika')},
        operation_description="Rejestracja nowego użytkownika. Domyślna rola to 'client'. Tylko manager może przypisać inną rolę."
    )
    def post(self, request):
        data = request.data.copy()
        if 'role' in data and data['role'] != 'client':
            if not request.user.is_authenticated or request.user.role != 'manager':
                raise PermissionDenied("Tylko manager może przypisywać role inne niż 'client'.")
        else:
            data['role'] = 'client'

        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Zwraca dane aktualnie zalogowanego użytkownika.",
        responses={200: UserSerializer}
    )
    def get(self, request):
        user = request.user
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
        operation_description="Zwraca listę wszystkich użytkowników. Dostęp tylko dla managera.",
        responses={200: UserSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsManager]

    @swagger_auto_schema(
        operation_description="Zwraca szczegóły użytkownika. Dostęp tylko dla managera.",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=UserSerializer,
        operation_description="Aktualizuje dane użytkownika. Dostęp tylko dla managera.",
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)