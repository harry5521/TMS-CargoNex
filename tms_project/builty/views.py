from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from .models import Builty
from customers.models import Customer
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Create your views here.


class BuiltyListView(ListView):
    model = Builty
    template_name = 'operations/builty_lr.html'
    context_object_name = 'builties'
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Builty.objects
            .select_related('customer')
            .order_by('-builty_date')
        )

        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(builty_no__icontains=search) |
                Q(customer__company_name__icontains=search) |
                Q(origin_city__icontains=search) |
                Q(destination_city__icontains=search)
            )

        filter_type = self.request.GET.get('filter')
        today = timezone.now().date()
        
        if filter_type == 'today':
            queryset = queryset.filter(
                builty_date=today
            )

        elif filter_type == 'yesterday':
            queryset = queryset.filter(
                builty_date=today - timedelta(days=1)
            )

        elif filter_type == 'week':
            queryset = queryset.filter(
                builty_date__gte=today - timedelta(days=7)
            )

        elif filter_type == 'month':
            queryset = queryset.filter(
                builty_date__month=today.month,
                builty_date__year=today.year
            )

        elif filter_type == 'range':
            start = self.request.GET.get(
                'start_date'
            )
            end = self.request.GET.get(
                'end_date'
            )

            if start and end:

                queryset = queryset.filter(
                    builty_date__range=[start, end]
                )

        return queryset


class BuiltyCreateView(View):

    def get(self, request):

        customers = Customer.objects.all().order_by('company_name')

        return render(
            request,
            'operations/builtyform.html',
            {
                'customers': customers
            }
        )

    def post(self, request):

        try:

            freight_amount = Decimal(
                request.POST.get('freight_amount') or 0
            )

            advance_amount = Decimal(
                request.POST.get('advance_amount') or 0
            )

            package_count = request.POST.get('package_count')
            if package_count == '':
                package_count = None

            if advance_amount <= 0:
                payment_status = 'topay'

            elif advance_amount >= freight_amount:
                payment_status = 'paid'

            else:
                payment_status = 'partial'

            customer = Customer.objects.get(
                pk=request.POST.get('customer')
            )

            Builty.objects.create(

                customer_id=request.POST.get('customer'),

                receiver_name=request.POST.get('receiver_name'),

                receiver_phone=request.POST.get('receiver_phone'),

                origin_city=request.POST.get('origin_city'),

                destination_city=request.POST.get('destination_city'),

                goods_description=request.POST.get('goods_description'),

                weight=request.POST.get('weight'),

                package_count=package_count,

                freight_amount=freight_amount,

                advance_amount=advance_amount,

                payment_status=payment_status,

                vehicle_number=request.POST.get('vehicle_number'),

                driver_name=request.POST.get('driver_name'),

                driver_phone=request.POST.get('driver_phone'),

                notes=request.POST.get('notes')
            )

            customer.current_balance += (
                freight_amount - advance_amount
            )

            customer.save(
                update_fields=['current_balance']
            )

            messages.success(
                request,
                'Builty created successfully.'
            )

            return redirect(
                'builty:builty_list'
            )

        except Exception as e:

            print(f'Error creating builty: {e}')
            messages.error(
                request,
                f'Error creating builty: {e}'
            )

            return redirect(
                'builty:builty_create'
            )
        


class CustomerSearchView(View):

    def get(self, request):

        q = request.GET.get('q', '').strip()

        if not q:
            return JsonResponse([], safe=False)

        customers = (
            Customer.objects
            .filter(
                company_name__icontains=q
            )
            .only(
                'id',
                'company_name',
                'phone',
                'cnic_ntn'
            )[:10]
        )

        data = []

        for customer in customers:

            data.append({
                'id': customer.id,
                'company_name': customer.company_name,
                'phone': customer.phone,
                'cnic': customer.cnic_ntn,
            })

        return JsonResponse(
            data,
            safe=False
        )