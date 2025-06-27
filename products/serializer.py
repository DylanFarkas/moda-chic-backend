import json
from rest_framework import serializers
from .models import Product, Category, ProductImage, ProductSizeStock, Size

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']
        
class ProductSizeStockSerializer(serializers.ModelSerializer):
    size = SizeSerializer()

    class Meta:
        model = ProductSizeStock
        fields = ['size', 'stock']
        
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
        
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = CategorySerializer(source='category', read_only=True)
    #image = serializers.ImageField(required=False, allow_null=True)
    size_stock = ProductSizeStockSerializer(many=True, read_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'