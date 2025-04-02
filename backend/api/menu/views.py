import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import MenuItem
from .permissions import IsManagerOrReadOnly, IsManagerOrKitchen
from .serializers import MenuItemSerializer

logger = logging.getLogger("audit")


class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]

    @swagger_auto_schema(
        operation_description="Returns the list of all menu items.",
        responses={200: MenuItemSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"{request.user} fetched menu item list.")
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=MenuItemSerializer,
        operation_description="Creates a new menu item. Only accessible to managers.",
        responses={201: MenuItemSerializer}
    )
    def post(self, request, *args, **kwargs):
        logger.info(f"{request.user} created a new menu item.")
        return super().post(request, *args, **kwargs)


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]

    @swagger_auto_schema(
        operation_description="Returns details of a specific menu item.",
        responses={200: MenuItemSerializer}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"{request.user} viewed menu item #{kwargs.get('pk')}")
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=MenuItemSerializer,
        operation_description="Updates a menu item. Only accessible to managers.",
        responses={200: MenuItemSerializer}
    )
    def patch(self, request, *args, **kwargs):
        logger.info(f"{request.user} updated menu item #{kwargs.get('pk')}")
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Deletes a menu item. Only accessible to managers.",
        responses={204: 'No content'}
    )
    def delete(self, request, *args, **kwargs):
        logger.info(f"{request.user} deleted menu item #{kwargs.get('pk')}")
        return super().delete(request, *args, **kwargs)


class ToggleAvailabilityView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrKitchen]

    @swagger_auto_schema(
        operation_description="Toggles the availability of a menu item. Available for managers and kitchen staff.",
        responses={
            200: openapi.Response(
                description="Item availability toggled successfully.",
                examples={
                    "application/json": {
                        "id": 1,
                        "name": "Pizza Margherita",
                        "available": False
                    }
                }
            ),
            404: "Item not found"
        }
    )
    def post(self, request, pk):
        try:
            item = MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            logger.warning(f"{request.user} tried to toggle unavailable item #{pk}")
            return Response({"detail": "Item not found"}, status=404)

        item.available = not item.available
        item.save()

        logger.info(f"{request.user} toggled availability for item #{pk} to {item.available}")

        return Response({
            "id": item.id,
            "name": item.name,
            "available": item.available
        })
