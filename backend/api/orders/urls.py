from django.urls import path
from .views import OrderListCreateView, OrderDetailView, OrderStatsView, ManagerOrderListView, KitchenOrderListView, WaiterOrderListView, OrderHistoryView

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('stats/', OrderStatsView.as_view(), name='order-stats'),
    path('manager/', ManagerOrderListView.as_view(), name='manager-orders'),
    path('kitchen/', KitchenOrderListView.as_view(), name='kitchen-orders'),
    path('waiter/', WaiterOrderListView.as_view(), name='waiter-orders'),
    path('<int:pk>/history/', OrderHistoryView.as_view(), name='order-history'),
]

