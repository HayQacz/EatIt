import logging
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

logger = logging.getLogger("audit")


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
        instance = serializer.save(user=self.request.user)
        logger.info(f"{self.request.user} created order #{instance.id}.")

    @swagger_auto_schema(
        operation_description="Returns orders depending on user role (client: own only, kitchen: new/in_progress, others: all).",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"{request.user} fetched order list.")
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=OrderSerializer,
        operation_description="Creates a new order. Default status is 'new'.",
        responses={201: OrderSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewOrder]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific order.",
        responses={200: OrderSerializer}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"{request.user} fetched order #{kwargs.get('pk')}.")
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, example='in_progress')
            },
        ),
        operation_description="Update order status. Only managers are allowed.",
        responses={200: OrderSerializer}
    )
    def patch(self, request, *args, **kwargs):
        if not CanModifyOrderStatus().has_permission(request, self):
            raise PermissionDenied("Only managers can change order status.")

        logger.info(f"{request.user} attempted to update status for order #{kwargs.get('pk')}.")
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.save()
        if 'status' in serializer.validated_data:
            OrderStatusHistory.objects.create(
                order=instance,
                status=instance.status,
                changed_by=self.request.user
            )
            logger.info(f"Order #{instance.id} status changed to {instance.status} by {self.request.user}.")


class OrderStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Returns order count grouped by status.",
        responses={200: openapi.Response(description="Order statistics")}
    )
    def get(self, request):
        stats = (
            Order.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        logger.info(f"{request.user} requested order statistics.")
        return Response({entry['status']: entry['count'] for entry in stats})


class ManagerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsManager]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_description="Returns a list of all orders (manager only).",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"Manager {request.user} accessed full order list.")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Order.objects.all()


class KitchenOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsKitchen]

    @swagger_auto_schema(
        operation_description="Returns orders to prepare (status: new, in_progress).",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"Kitchen user {request.user} accessed kitchen orders.")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Order.objects.filter(status__in=['new', 'in_progress']).order_by('-created_at')


class WaiterOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsWaiter]

    @swagger_auto_schema(
        operation_description="Returns orders ready to serve (waiter view).",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"Waiter {request.user} accessed ready orders.")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Order.objects.filter(status='ready').order_by('-created_at')


class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderStatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Returns status history for a specific order.",
        responses={200: OrderStatusHistorySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"{request.user} requested status history for order #{kwargs.get('pk')}.")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        order_id = self.kwargs['pk']
        return OrderStatusHistory.objects.filter(order_id=order_id)
