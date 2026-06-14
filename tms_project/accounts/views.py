from django.db.models import Q, Sum
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

from .models import Transaction, TransactionCategory


class AccountsView(ListView):

    model = Transaction
    template_name = 'accounts/accounts.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):

        queryset = (
            Transaction.objects
            .select_related(
                'category',
                'customer',
                'builty'
            )
            .order_by('-transaction_date', '-id')
        )

        search = self.request.GET.get('search')
        txn_type = self.request.GET.get('type')
        category = self.request.GET.get('category')

        if search:
            queryset = queryset.filter(
                Q(transaction_id__icontains=search) |
                Q(description__icontains=search) |
                Q(customer__company_name__icontains=search) |
                Q(builty__builty_no__icontains=search)
            )

        if txn_type:
            queryset = queryset.filter(
                transaction_type=txn_type
            )

        if category:
            queryset = queryset.filter(
                category_id=category
            )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        transactions = Transaction.objects.all()

        cash_in = (
            transactions
            .filter(transaction_type='cash_in')
            .aggregate(total=Sum('amount'))
            ['total']
            or 0
        )

        cash_out = (
            transactions
            .filter(transaction_type='cash_out')
            .aggregate(total=Sum('amount'))
            ['total']
            or 0
        )

        context['balance'] = cash_in - cash_out
        context['cash_in'] = cash_in
        context['cash_out'] = cash_out

        context['categories'] = (
            TransactionCategory.objects
            .filter(is_active=True)
            .order_by('name')
        )

        context['search'] = self.request.GET.get(
            'search',
            ''
        )

        context['selected_type'] = self.request.GET.get(
            'type',
            ''
        )

        context['selected_category'] = self.request.GET.get(
            'category',
            ''
        )

        return context
    
class PaymentsView(View):
    def get(self, request):
        return render(request, 'accounts/payments.html')

