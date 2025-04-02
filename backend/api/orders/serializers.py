from rest_framework import serializers
from core.models import Order, OrderItem, MenuItem


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity', 'comment']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'updated_at', 'items', 'table_number', 'notes']
        read_only_fields = ['user', 'created_at', 'updated_at', 'status']


    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(user=self.context['request'].user, **validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order
