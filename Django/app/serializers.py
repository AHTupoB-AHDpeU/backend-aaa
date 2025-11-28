from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from .models import Service, Review, Rating, Order
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=30)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name')
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Пароль должен содержать хотя бы одну цифру")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует") # ИСКЛЮЧЕНИЕ
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                raise serializers.ValidationError("Аккаунт неактивен")
            raise serializers.ValidationError("Неверные учетные данные") # ИСКЛЮЧЕНИЕ
        else:
            raise serializers.ValidationError("Необходимо указать email и пароль")

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'picture', 'price', 'description')

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('id', 'name', 'value')

class ReviewSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    rating_value = serializers.FloatField(source='rating.value', read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'user', 'user_first_name', 'user_username', 'service', 
                 'service_name', 'rating', 'rating_value', 'date', 'description')

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('service', 'rating', 'description')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['date'] = timezone.now().date()
        return super().create(validated_data)

class OrderSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    services_details = serializers.SerializerMethodField()  # Изменили название
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'user_name', 'user_full_name', 'user_email', 
                 'services_details', 'address', 'total_cost', 'created_at', 
                 'status', 'status_display')
        read_only_fields = ('user', 'services', 'address', 'total_cost', 'created_at')

    def get_user_name(self, obj):
        return obj.user.username

    def get_user_full_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        elif obj.user.first_name:
            return obj.user.first_name
        else:
            return obj.user.username

    def get_services_details(self, obj):
        """Возвращает детальную информацию об услугах"""
        services = obj.services.all()
        return [{
            'id': service.id,
            'name': service.name,
            'price': service.price,
            'description': service.description
        } for service in services]

class OrderCreateSerializer(serializers.ModelSerializer):
    services = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = Order
        fields = ('services', 'address', 'total_cost')

    def create(self, validated_data):
        services_ids = validated_data.pop('services')
        user = self.context['request'].user
        
        order = Order.objects.create(
            user=user,
            address=validated_data['address'],
            total_cost=validated_data['total_cost']
        )
        
        services = Service.objects.filter(id__in=services_ids)
        order.services.set(services)
        
        return order