from rest_framework import generics, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import MenuItem
from .serializers import MenuItemSerializer
from .permissions import IsManagerOrReadOnly


class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]

    @swagger_auto_schema(
        operation_description="Zwraca listę wszystkich pozycji w menu.",
        responses={200: MenuItemSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=MenuItemSerializer,
        operation_description="Tworzy nową pozycję w menu. Dostępne tylko dla managera.",
        responses={201: MenuItemSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]

    @swagger_auto_schema(
        operation_description="Zwraca szczegóły pojedynczej pozycji w menu.",
        responses={200: MenuItemSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=MenuItemSerializer,
        operation_description="Aktualizuje pozycję w menu. Dostępne tylko dla managera.",
        responses={200: MenuItemSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Usuwa pozycję z menu. Dostępne tylko dla managera.",
        responses={204: 'No content'}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)