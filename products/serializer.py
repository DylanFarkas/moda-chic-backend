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
    image = serializers.SerializerMethodField()
    class Meta:
        model = ProductImage
        fields = ['id', 'image']
        
    def get_image(self, obj):
        return obj.image.url if obj.image else None
        
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = CategorySerializer(source='category', read_only=True)
    #image = serializers.ImageField(required=False, allow_null=True)
    size_stock = ProductSizeStockSerializer(many=True, read_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    
    main_image = serializers.ImageField(required=False, allow_null=True)



    class Meta:
        model = Product
        fields = [
        'id', 'name', 'description', 'price', 'material',
        'main_image', 'category', 'category_name',
        'created_at', 'size_stock', 'additional_images',
        'average_rating',
    ]
        
    def get_main_image(self, obj):
        return obj.main_image.url if obj.main_image else None
    
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.main_image:
            data['main_image'] = instance.main_image.url
        else:
            data['main_image'] = None
        return data