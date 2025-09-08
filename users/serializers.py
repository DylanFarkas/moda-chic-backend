from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import Order, OrderItem
from products.models import ProductSizeStock
from .models import Cart, CartItem, Order, OrderItem, Review, User, Wishlist
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
    

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    size_name = serializers.CharField(source='size.name', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'size', 'size_name', 'quantity', 'price', 'total']
        
    def get_total(self, obj):
        return round(obj.product.price * obj.quantity, 2)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_order = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'nombre', 'email', 'telefono', 'departamento', 'ciudad', 'direccion', 'created_at', 'items', 'status', 'total_order']
        
    def get_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        return OrderItemSerializer(order_items, many=True).data
    
    def get_total_order(self, obj):
        return round(sum(item.product.price * item.quantity for item in obj.items.all()), 2)


    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # Verificar stock antes de crear la orden
        for item in items_data:
            product = item['product']
            size = item['size']
            quantity = item['quantity']

            stock_item = ProductSizeStock.objects.get(product=product, size=size)
            if stock_item.stock < quantity:
                raise serializers.ValidationError(
                    f"Stock insuficiente para {product.name} talla {size.name}"
                )

        # Crear la orden
        order = Order.objects.create(**validated_data)

        # Crear items y descontar stock
        for item in items_data:
            product = item['product']
            size = item['size']
            quantity = item['quantity']

            OrderItem.objects.create(
                order=order,
                product=product,
                size=size,
                quantity=quantity
            )

            stock_item = ProductSizeStock.objects.get(product=product, size=size)
            stock_item.stock -= quantity
            stock_item.save()

        return order

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at', 'user', 'user_name']
        
