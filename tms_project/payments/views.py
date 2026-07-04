from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from .models import Payment
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

class PaymentListView(ListView):
    model = Payment
    template_name = 'accounts/payments.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Payment.objects.select_related('builty', 'builty__customer').order_by('-created_at')
        
        # 1. Text Search (ID, Customer Name, Builty No)
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(payment_id__icontains=search_query) |
                Q(builty__customer__name__icontains=search_query) |
                Q(builty__builty_no__icontains=search_query)
            )

        # 2. Payment Mode Filter
        payment_mode = self.request.GET.get('payment_mode', '').strip()
        if payment_mode:
            queryset = queryset.filter(payment_mode=payment_mode)

        # 3. Dynamic Date Period Filter
        date_period = self.request.GET.get('date_period', 'all').strip()
        today = timezone.localdate()

        if date_period == 'today':
            queryset = queryset.filter(payment_date=today)
            
        elif date_period == 'yesterday':
            yesterday = today - timedelta(days=1)
            queryset = queryset.filter(payment_date=yesterday)
            
        elif date_period == 'this_week':
            # Current week ka start (Monday) nikalne k liye
            start_of_week = today - timedelta(days=today.weekday())
            queryset = queryset.filter(payment_date__gte=start_of_week, payment_date__lte=today)
            
        elif date_period == 'this_month':
            queryset = queryset.filter(payment_date__year=today.year, payment_date__month=today.month)
            
        elif date_period == 'custom':
            start_date = self.request.GET.get('start_date', '').strip()
            end_date = self.request.GET.get('end_date', '').strip()
            if start_date:
                queryset = queryset.filter(payment_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(payment_date__lte=end_date)

        return queryset