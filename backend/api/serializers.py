from rest_framework import serializers
from api.models import AppUser, UserQuery

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'username', 'email', 'password']

class UserQuerySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = UserQuery
        fields = ['id', 'user', 'query', 'created_at']
