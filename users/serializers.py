from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Cart, CartItem, User, Wishlist
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import re

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_admin', 'is_customer']  


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def validate_password(self, value):
        # Mínimo 6 caracteres
        if len(value) < 6:
            raise serializers.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        # Al menos un caracter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("La contraseña debe contener al menos un caracter especial (!@#$%^&*(),.?\":{}|<>).")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_customer=True
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Credenciales inválidas")


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    
class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_name', 'product_price', 'product_image']
        read_only_fields = ['user']

    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

    def get_product_price(self, obj):
        return obj.product.price if obj.product else None

    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product and obj.product.main_image:
            return request.build_absolute_uri(obj.product.main_image.url)
        return None
    
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    size_name = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'size', 'quantity', 'product_name', 'product_price', 'product_image', 'size_name']
        read_only_fields = ['cart']

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_price(self, obj):
        return obj.product.price

    def get_size_name(self, obj):
        return obj.size.name
    
    def get_product_image(self, obj):
        request = self.context.get('request')
        if obj.product and obj.product.main_image:
            return request.build_absolute_uri(obj.product.main_image.url)
        return None

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_price']
        read_only_fields = ['user']

    def get_total_price(self, obj):
        return obj.total_price()