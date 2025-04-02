from django.urls import path, include
from swagger_urls import urlpatterns as swagger_urls

urlpatterns = [
    path('api/', include('api.urls')),
] + swagger_urls
