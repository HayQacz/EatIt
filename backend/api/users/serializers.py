from rest_framework import serializers
from core.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'role': {'read_only': True}
        }

    def create(self, validated_data):
        request = self.context.get('request')
        user_role = 'client'

        if request and request.user.is_authenticated and request.user.role == 'manager':
            user_role = self.initial_data.get('role', 'client')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=user_role
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']