from django.views.generic import ListView
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import (
    Transaction,
    TransactionCategory,
)
import logging
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views import View

from builty.models import Builty
from customers.models import Customer

from .models import Payment


logger = logging.getLogger(__name__)


class PaymentListView(ListView):
    model = Payment
    template_name = "accounts/payments.html"
    context_object_name = "payments"
    paginate_by = 10

    def get_queryset(self):
        queryset = Payment.objects.select_related(
            "builty", "builty__customer"
        ).order_by("-created_at")

        # 1. Text Search (ID, Customer Name, Builty No)
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(payment_id__icontains=search_query)
                | Q(builty__customer__company_name__icontains=search_query)
                | Q(builty__builty_no__icontains=search_query)
            )

        # 2. Payment Mode Filter
        payment_mode = self.request.GET.get("payment_mode", "").strip()
        if payment_mode:
            queryset = queryset.filter(payment_mode=payment_mode)

        # 3. Dynamic Date Period Filter
        date_period = self.request.GET.get("date_period", "all").strip()
        today = timezone.localdate()

        if date_period == "today":
            queryset = queryset.filter(payment_date=today)

        elif date_period == "yesterday":
            yesterday = today - timedelta(days=1)
            queryset = queryset.filter(payment_date=yesterday)

        elif date_period == "this_week":
            # Current week ka start (Monday) nikalne k liye
            start_of_week = today - timedelta(days=today.weekday())
            queryset = queryset.filter(
                payment_date__gte=start_of_week, payment_date__lte=today
            )

        elif date_period == "this_month":
            queryset = queryset.filter(
                payment_date__year=today.year, payment_date__month=today.month
            )

        elif date_period == "custom":
            start_date = self.request.GET.get("start_date", "").strip()
            end_date = self.request.GET.get("end_date", "").strip()
            if start_date:
                queryset = queryset.filter(payment_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(payment_date__lte=end_date)

        return queryset




class PaymentCreateView(View):

    def post(self, request):
        redirect_url = reverse("payments:payments_view")

        try:
            with transaction.atomic():

                # -------------------------
                # Raw Form Data
                # -------------------------

                builty_id = request.POST.get("builty", "").strip()
                raw_amount = request.POST.get("amount", "").strip()
                payment_mode = request.POST.get("payment_mode", "").strip()
                raw_payment_date = request.POST.get("payment_date", "").strip()
                reference_no = request.POST.get("reference_no", "").strip()
                remarks = request.POST.get("remarks", "").strip()

                # -------------------------
                # Basic Validation
                # -------------------------

                if not builty_id:
                    raise ValidationError(
                        "Please select a valid Builty."
                    )

                try:
                    amount = Decimal(raw_amount)
                except (InvalidOperation, TypeError):
                    raise ValidationError(
                        "Please enter a valid payment amount."
                    )

                if amount <= 0:
                    raise ValidationError(
                        "Payment amount must be greater than zero."
                    )

                valid_modes = {
                    value
                    for value, _ in Payment.PAYMENT_MODES
                }

                if payment_mode not in valid_modes:
                    raise ValidationError(
                        "Please select a valid payment mode."
                    )

                payment_date = parse_date(raw_payment_date)

                if not payment_date:
                    raise ValidationError(
                        "Please select a valid payment date."
                    )

                if payment_mode != "cash" and not reference_no:
                    raise ValidationError(
                        "Reference number is required for non-cash payments."
                    )

                # -------------------------
                # Lock Builty
                # -------------------------

                try:
                    builty = (
                        Builty.objects
                        .select_for_update()
                        .select_related("customer")
                        .get(pk=builty_id)
                    )
                except Builty.DoesNotExist:
                    raise ValidationError(
                        "Selected Builty does not exist."
                    )

                # Explicitly lock Customer balance row
                customer = (
                    Customer.objects
                    .select_for_update()
                    .get(pk=builty.customer_id)
                )

                # -------------------------
                # Authoritative Validation
                # -------------------------

                outstanding = Decimal(
                    builty.remaining_amount
                )

                if (
                    builty.payment_status == "paid"
                    or outstanding <= 0
                ):
                    raise ValidationError(
                        "This Builty has already been fully paid."
                    )

                if amount > outstanding:
                    raise ValidationError(
                        "Payment amount cannot exceed the outstanding amount."
                    )

                current_customer_balance = (
                    customer.current_balance
                    or Decimal("0")
                )

                if amount > current_customer_balance:
                    raise ValidationError(
                        "Payment amount cannot exceed the customer's current balance."
                    )

                try:
                    category = (
                        TransactionCategory.objects
                        .get(name__iexact="Customer Payment")
                    )
                except TransactionCategory.DoesNotExist:
                    raise ValidationError(
                        'The "Customer Payment" transaction category is missing.'
                    )

                # -------------------------
                # Create Payment
                # -------------------------

                payment = Payment.objects.create(
                    builty=builty,
                    amount=amount,
                    payment_mode=payment_mode,
                    payment_date=payment_date,
                    reference_no=reference_no or None,
                    remarks=remarks or None,
                )

                # -------------------------
                # Update Customer Balance
                # -------------------------

                customer.current_balance = (
                    current_customer_balance - amount
                )

                customer.save(
                    update_fields=["current_balance"]
                )

                # -------------------------
                # Update Builty
                # -------------------------

                builty.advance_amount = (
                    Decimal(builty.advance_amount)
                    + amount
                )

                builty.remaining_amount = (
                    Decimal(builty.freight_amount)
                    - builty.advance_amount
                )

                if builty.remaining_amount <= 0:
                    builty.remaining_amount = Decimal("0")
                    builty.payment_status = "paid"
                else:
                    builty.payment_status = "partial"

                builty.save(
                    update_fields=[
                        "advance_amount",
                        "remaining_amount",
                        "payment_status",
                    ]
                )

                # -------------------------
                # Create Ledger Entry
                # -------------------------

                Transaction.objects.create(
                    title=f"Payment against {builty.builty_no}",
                    transaction_type=category.cash_flow,
                    category=category,
                    customer=customer,
                    builty=builty,
                    amount=amount,
                    remarks=remarks or None,
                )

                messages.success(
                    request,
                    f"Payment {payment.payment_id} recorded successfully."
                )

        except ValidationError as exc:
            messages.error(
                request,
                exc.messages[0]
            )

        except Exception:
            logger.exception(
                "Unexpected error while recording payment."
            )

            messages.error(
                request,
                "Unable to record payment. Please try again."
            )

        if request.POST.get("add_another") == "1":
            return redirect(
                f"{redirect_url}?open_payment=1"
            )

        return redirect(redirect_url)


# Builty Searchable field for payment creation
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def search_builties(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    builties = (
        Builty.objects
        .select_related("customer")
        .filter(
            Q(builty_no__icontains=query)
            | Q(customer__company_name__icontains=query)
        )
        .order_by("-created_at")[:10]
    )

    results = [
        {
            "id": builty.id,
            "builty_no": builty.builty_no,
            "customer_name": builty.customer.company_name,
            "total_freight": float(builty.freight_amount),
            "advance_paid": float(builty.advance_amount),
            "outstanding": float(builty.remaining_amount),
            "payment_status": builty.payment_status,
        }
        for builty in builties
    ]

    return JsonResponse(results, safe=False)