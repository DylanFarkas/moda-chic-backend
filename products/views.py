from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .serializer import ProductSerializer, CategorySerializer, SizeSerializer
from .models import Product, Category, Size, ProductSizeStock
import json

class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by("id")
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        product = serializer.save()

        # Obtener y parsear el JSON con tallas y stock
        sizes_json = self.request.data.get("sizes_json")
        if sizes_json:
            try:
                size_stock_data = json.loads(sizes_json)
                for item in size_stock_data:
                    size_name = item.get("size")
                    stock = item.get("stock")

                    try:
                        size = Size.objects.get(name=size_name)
                        ProductSizeStock.objects.create(
                            product=product,
                            size=size,
                            stock=stock
                        )
                    except Size.DoesNotExist:
                        continue  # O podrías lanzar un error personalizado
            except json.JSONDecodeError:
                pass  # Manejo opcional de error
    
    def perform_update(self, serializer):
        product = serializer.save()

        # Obtener y parsear el JSON con las tallas y stock para actualizar
        sizes_json = self.request.data.get("sizes_json")
        if sizes_json:
            try:
                size_stock_data = json.loads(sizes_json)

                # Eliminar las tallas actuales asociadas al producto antes de agregar las nuevas
                product.size_stock.all().delete()

                for item in size_stock_data:
                    size_name = item.get("size")
                    stock = item.get("stock")

                    try:
                        size = Size.objects.get(name=size_name)
                        ProductSizeStock.objects.create(
                            product=product,
                            size=size,
                            stock=stock
                        )
                    except Size.DoesNotExist:
                        continue  # O podrías lanzar un error personalizado

            except json.JSONDecodeError:
                pass  # Manejo opcional de error
            

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("id")
    
class SizeView(viewsets.ModelViewSet):
    serializer_class = SizeSerializer
    queryset = Size.objects.all().order_by("id")
