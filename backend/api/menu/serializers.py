from rest_framework import serializers
from core.models import MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'available', 'image']

