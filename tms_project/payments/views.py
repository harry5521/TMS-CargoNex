import logging
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.dateparse import parse_date
from django.views import View
from django.views.decorators.http import require_GET
from django.views.generic import ListView

from builty.models import Builty

from .models import Payment
from .services import record_builty_payment


logger = logging.getLogger(__name__)


class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "accounts/payments.html"
    context_object_name = "payments"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Payment.objects
            .select_related("builty", "builty__customer")
            .order_by("-created_at")
        )

        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(payment_id__icontains=search_query)
                | Q(
                    builty__customer__company_name__icontains=search_query
                )
                | Q(builty__builty_no__icontains=search_query)
            )

        payment_mode = self.request.GET.get("payment_mode", "").strip()
        if payment_mode:
            queryset = queryset.filter(payment_mode=payment_mode)

        date_period = self.request.GET.get("date_period", "all").strip()
        today = timezone.localdate()

        if date_period == "today":
            queryset = queryset.filter(payment_date=today)

        elif date_period == "yesterday":
            queryset = queryset.filter(
                payment_date=today - timedelta(days=1)
            )

        elif date_period == "this_week":
            start_of_week = today - timedelta(days=today.weekday())
            queryset = queryset.filter(
                payment_date__gte=start_of_week,
                payment_date__lte=today,
            )

        elif date_period == "this_month":
            queryset = queryset.filter(
                payment_date__year=today.year,
                payment_date__month=today.month,
            )

        elif date_period == "custom":
            start_date = self.request.GET.get("start_date", "").strip()
            end_date = self.request.GET.get("end_date", "").strip()

            if start_date:
                queryset = queryset.filter(payment_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(payment_date__lte=end_date)

        return queryset


class PaymentCreateView(LoginRequiredMixin, View):

    def post(self, request):
        redirect_url = reverse("payments:payments_view")

        try:
            builty_id = request.POST.get("builty", "").strip()
            raw_amount = request.POST.get("amount", "").strip()
            payment_mode = request.POST.get("payment_mode", "").strip()
            raw_payment_date = request.POST.get(
                "payment_date", ""
            ).strip()
            reference_no = request.POST.get("reference_no", "").strip()
            remarks = request.POST.get("remarks", "").strip()

            if not builty_id:
                raise ValidationError("Please select a valid Builty.")

            try:
                amount = Decimal(raw_amount)
            except (InvalidOperation, TypeError):
                raise ValidationError(
                    "Please enter a valid payment amount."
                )

            payment_date = parse_date(raw_payment_date)
            if not payment_date:
                raise ValidationError(
                    "Please select a valid payment date."
                )

            payment, _ = record_builty_payment(
                builty=builty_id,
                amount=amount,
                payment_mode=payment_mode,
                payment_date=payment_date,
                reference_no=reference_no or None,
                remarks=remarks or None,
            )

            messages.success(
                request,
                f"Payment {payment.payment_id} recorded successfully.",
            )

        except ValidationError as exc:
            messages.error(request, exc.messages[0])

        except Exception:
            logger.exception(
                "Unexpected error while recording payment."
            )
            messages.error(
                request,
                "Unable to record payment. Please try again.",
            )

        if request.POST.get("add_another") == "1":
            return redirect(f"{redirect_url}?open_payment=1")

        return redirect(redirect_url)


@require_GET
def search_builties(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    builties = (
        Builty.objects
        .select_related("customer")
        .filter(
            document_status="finalized",
            remaining_amount__gt=0,
        )
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
