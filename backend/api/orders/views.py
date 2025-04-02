from django.db.models import Count
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import Order, OrderStatusHistory
from .serializers import OrderSerializer, OrderStatusHistorySerializer
from .permissions import CanViewOrder, CanModifyOrderStatus, IsManager, IsKitchen, IsWaiter


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.all()

        if user.role == 'client':
            queryset = queryset.filter(user=user)
        elif user.role == 'kitchen':
            queryset = queryset.filter(status__in=['new', 'in_progress'])

        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        created_after = self.request.query_params.get('created_after')
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)

        created_before = self.request.query_params.get('created_before')
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Zwraca listę zamówień wg roli użytkownika (client: tylko swoje, kitchen: new/in_progress, reszta: wszystkie).",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=OrderSerializer,
        operation_description="Tworzy nowe zamówienie. Domyślnie status to 'new'.",
        responses={201: OrderSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewOrder]

    @swagger_auto_schema(
        operation_description="Zwraca szczegóły pojedynczego zamówienia.",
        responses={200: OrderSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, example='in_progress')
            },
        ),
        operation_description="Zmienia status zamówienia. Dozwolone tylko dla managera.",
        responses={200: OrderSerializer}
    )
    def patch(self, request, *args, **kwargs):
        if not CanModifyOrderStatus().has_permission(request, self):
            raise PermissionDenied("Only managers can change order status.")
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.save()
        if 'status' in serializer.validated_data:
            OrderStatusHistory.objects.create(
                order=instance,
                status=instance.status,
                changed_by=self.request.user
            )


class OrderStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Zwraca liczbę zamówień w podziale na statusy.",
        responses={200: openapi.Response(description="Statystyki zamówień")}
    )
    def get(self, request):
        stats = (
            Order.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        return Response({entry['status']: entry['count'] for entry in stats})


class ManagerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsManager]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_description="Lista wszystkich zamówień dostępna dla managera.",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Order.objects.all()


class KitchenOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsKitchen]

    @swagger_auto_schema(
        operation_description="Lista zamówień dla kuchni (status: new, in_progress).",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Order.objects.filter(status__in=['new', 'in_progress']).order_by('-created_at')


class WaiterOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsWaiter]

    @swagger_auto_schema(
        operation_description="Lista zamówień gotowych do wydania (dla kelnera).",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Order.objects.filter(status='ready').order_by('-created_at')

class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderStatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs['pk']
        return OrderStatusHistory.objects.filter(order_id=order_id)