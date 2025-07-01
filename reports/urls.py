from django.urls import path
from .views import sales_report, top_products_report

urlpatterns = [
    path('sales/', sales_report, name='sales_report'),
    path('top-products/', top_products_report, name='top_products_report'),
]
