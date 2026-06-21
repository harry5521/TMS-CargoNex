from django.db.models import Q, Sum
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from .models import Transaction, TransactionCategory
from decimal import Decimal


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
                Q(remarks__icontains=search) |
                Q(category__name__icontains=search) |
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
            TransactionCategory.objects.all().order_by('name')
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
    

class TransactionCategorySaveView(View):

    def post(self, request):

        category_id = request.POST.get(
            'category_id'
        )

        name = request.POST.get(
            'name'
        )

        if category_id:

            category = TransactionCategory.objects.get(
                pk=category_id
            )

            category.name = name
            category.save()

        else:

            TransactionCategory.objects.create(
                name=name
            )

        return JsonResponse({
            'success': True
        })


class TransactionCreateView(View):

    def post(self, request):

        try:

            transaction_types = request.POST.getlist(
                'transaction_type'
            )

            categories = request.POST.getlist(
                'category'
            )

            amounts = request.POST.getlist(
                'amount'
            )

            remarks_list = request.POST.getlist(
                'remarks'
            )

            for i in range(
                len(transaction_types)
            ):

                if (
                    not categories[i]
                    or
                    not amounts[i]
                ):
                    continue

                Transaction.objects.create(

                    transaction_type=
                    transaction_types[i],

                    category_id=
                    categories[i],

                    amount=
                    Decimal(amounts[i]),

                    remarks=
                    remarks_list[i]
                )

            messages.success(
                request,
                'Transactions added successfully.'
            )

        except Exception as e:

            messages.error(
                request,
                f'Error: {e}'
            )

        return redirect(
            'accounts:accounts'
        )

class PaymentsView(View):
    def get(self, request):
        return render(request, 'accounts/payments.html')

