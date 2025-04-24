from django.shortcuts import render
from rest_framework import viewsets
from .serializer import ProductSerializer, CategorySerializer
from .models import Product, Category

# Create your views here.
class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by("id")

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("id")
