from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from django.db.models import Q
from .models import Customer

# Create your views here.

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customers.html'
    context_object_name = 'customers'
    paginate_by = 10

    def get_queryset(self):
        queryset = Customer.objects.all().order_by('-id')
        search = self.request.GET.get('search', '').strip()

        if search:
            queryset = queryset.filter(
                Q(customer_id__icontains=search) |
                Q(company_name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(phone__icontains=search)
            )
        return queryset


class CustomerFormView(LoginRequiredMixin, View):

    def get(self, request):
        return render(
            request,
            'customers/customer_form.html'
        )

    def post(self, request):

        try:

            Customer.objects.create(
                company_name=request.POST.get('company_name'),
                contact_person=request.POST.get('contact_person'),
                phone=request.POST.get('phone'),
                cnic_ntn=request.POST.get('cnic_ntn'),
                address=request.POST.get('address'),
                notes=request.POST.get('notes'),
                customer_type=request.POST.get('customer_type')
            )

            messages.success(
                request,
                'Customer created successfully.'
            )

            return redirect('customers:customers-list')

        except Exception as e:

            messages.error(
                request,
                f'Error creating customer: {e}'
            )

            return redirect(
                'customers:customer-create'
            )



class CustomerUpdateView(LoginRequiredMixin, View):

    def post(self, request, pk):

        customer = get_object_or_404(
            Customer,
            pk=pk
        )

        try:

            customer.company_name = request.POST.get(
                'company_name',
                ''
            ).strip()

            customer.contact_person = request.POST.get(
                'contact_person',
                ''
            ).strip()

            customer.phone = request.POST.get(
                'phone'
            )

            customer.cnic_ntn = request.POST.get(
                'cnic_ntn'
            )

            customer.address = request.POST.get(
                'address'
            )

            customer.notes = request.POST.get(
                'notes'
            )

            customer.customer_type = request.POST.get(
                'customer_type'
            )

            customer.save()

            messages.success(
                request,
                'Customer updated successfully.'
            )

        except Exception as e:

            messages.error(
                request,
                f'Error updating customer: {e}'
            )

        return redirect(
            'customers:customers-list'
        )