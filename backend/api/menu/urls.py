from django.urls import path
from .views import MenuItemListCreateView, MenuItemDetailView

urlpatterns = [
    path('items/', MenuItemListCreateView.as_view(), name='menu-item-list-create'),
    path('items/<int:pk>/', MenuItemDetailView.as_view(), name='menu-item-detail'),
]
