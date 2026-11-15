"""Painel apenas para proprietário. Todas as métricas consultam o banco PostgreSQL."""
from datetime import timedelta
from decimal import Decimal
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from .models import Order, Product, Favorite

_original_index = admin.site.index

def hyper_index(request, extra_context=None):
    if not request.user.is_superuser:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    start = timezone.localdate() - timedelta(days=6)
    aggregated = (Order.objects.filter(status=Order.PAID, created_at__date__gte=start)
        .annotate(day=TruncDate('created_at'))
        .values('day').annotate(total=Sum('total')))
    by_day = {row['day']: row['total'] or Decimal('0') for row in aggregated}
    daily = [{'date': (start + timedelta(days=i)).strftime('%d/%m'),
              'total': by_day.get(start + timedelta(days=i), Decimal('0'))}
             for i in range(7)]
    maximum = max((x['total'] for x in daily), default=Decimal('0'))
    for day in daily:
        day['height'] = round(day['total'] / maximum * 100) if maximum else 0

    context = {
        'revenue': Order.objects.filter(status=Order.PAID).aggregate(total=Sum('total'))['total'] or Decimal('0'),
        'paid_orders': Order.objects.filter(status=Order.PAID).count(),
        'pending_orders': Order.objects.filter(status=Order.PENDING).count(),
        'customers': get_user_model().objects.filter(is_superuser=False).count(),
        'active_products': Product.objects.filter(active=True).count(),
        'low_stock': Product.objects.filter(active=True,stock__lte=5).count(),
        'favorites_count': Favorite.objects.count(),
        'recent_orders': Order.objects.select_related('user').order_by('-created_at')[:5],
        'sales_days': daily,
    }
    context.update(extra_context or {})
    return _original_index(request, extra_context=context)

admin.site.index = hyper_index
