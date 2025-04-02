from django.urls import path
from .views import MenuItemListCreateView, MenuItemDetailView, ToggleAvailabilityView

urlpatterns = [
    path('items/', MenuItemListCreateView.as_view(), name='menu-item-list-create'),
    path('items/<int:pk>/', MenuItemDetailView.as_view(), name='menu-item-detail'),
    path('items/<int:pk>/toggle-availability/', ToggleAvailabilityView.as_view(), name='toggle-availability'),
]
