from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .serializer import ProductSerializer, CategorySerializer, SizeSerializer
from .models import Product, Category, Size, ProductImage, ProductSizeStock


import json

class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by("id")
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        product = serializer.save()

        # Tallas y stock
        sizes_json = self.request.data.get("sizes_json")
        if sizes_json:
            try:
                size_stock_data = json.loads(sizes_json)
                for item in size_stock_data:
                    size = Size.objects.get(name=item["size"])
                    ProductSizeStock.objects.create(product=product, size=size, stock=item["stock"])
            except Exception:
                pass

        # Imágenes adicionales
        additional_images = self.request.FILES.getlist("additional_images")
        for image in additional_images:
            ProductImage.objects.create(product=product, image=image)

    def perform_update(self, serializer):
        product = serializer.save()

        # Tallas y stock
        sizes_json = self.request.data.get("sizes_json")
        if sizes_json:
            try:
                product.size_stock.all().delete()
                size_stock_data = json.loads(sizes_json)
                for item in size_stock_data:
                    size = Size.objects.get(name=item["size"])
                    ProductSizeStock.objects.create(product=product, size=size, stock=item["stock"])
            except Exception:
                pass

        # Reemplazar imágenes adicionales si se suben nuevas
        additional_images = self.request.FILES.getlist("additional_images")
        if additional_images:
            product.additional_images.all().delete()
            for image in additional_images:
                ProductImage.objects.create(product=product, image=image)
            

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("id")
    
class SizeView(viewsets.ModelViewSet):
    serializer_class = SizeSerializer
    queryset = Size.objects.all().order_by("id")

