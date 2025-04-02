from django.urls import path, include

urlpatterns = [
    path('users/', include('api.users.urls')),
    path('menu/', include('api.menu.urls')),
    path('orders/', include('api.orders.urls')),
]
