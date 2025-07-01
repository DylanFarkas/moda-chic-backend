from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, F
from users.models import Order, OrderItem

@api_view(['GET'])
#@permission_classes([IsAdminUser])
def sales_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return Response({
            "error": "Debe proporcionar start_date y end_date en el formato YYYY-MM-DD"
        }, status=400)

    try:
        # Filtrar órdenes por fecha y estado
        valid_statuses = ['paid', 'shipped', 'delivered']
        orders = Order.objects.filter(
            created_at__date__range=[start_date, end_date],
            status__in=valid_statuses
        )
        order_ids = orders.values_list('id', flat=True)

        total_orders = orders.count()

        total_sales = OrderItem.objects.filter(order_id__in=order_ids).aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )['total'] or 0

        return Response({
            "start_date": start_date,
            "end_date": end_date,
            "total_orders": total_orders,
            "total_sales": total_sales,
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=500)


@api_view(['GET'])
#@permission_classes([IsAdminUser])
def top_products_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    valid_statuses = ['paid', 'shipped', 'delivered']
    order_items = OrderItem.objects.filter(order__status__in=valid_statuses)

    if start_date and end_date:
        order_items = order_items.filter(order__created_at__date__range=[start_date, end_date])

    top_products = (
        order_items
        .values('product__name', 'product__price')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:10]
    )

    return Response([
        {
            "product": p['product__name'],
            "price": p['product__price'],
            "sold": p['total_sold'],
            "total": round(p['product__price'] * p['total_sold'], 2)
        } for p in top_products
    ])