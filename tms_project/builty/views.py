import logging
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from customers.models import Customer
from drivers.models import Driver
from vehicles.models import Vehicle

from .forms import BuiltyForm
from .models import Builty
from .services import cancel_builty, finalize_builty


logger = logging.getLogger(__name__)


def add_form_errors_to_messages(request, form):
    for field_name, errors in form.errors.items():
        if field_name == "__all__":
            label = "Error"
        else:
            label = (
                form.fields[field_name].label
                or field_name.replace("_", " ").title()
            )

        for error in errors:
            messages.error(request, f"{label}: {error}")


def decimal_string(value):
    return str(value if value is not None else Decimal("0.00"))


def date_payload(value):
    if not value:
        return {"value": "", "display": "—"}

    return {
        "value": value.isoformat(),
        "display": value.strftime("%d %b %Y"),
    }

def add_validation_errors_to_messages(request, exc):

    if hasattr(exc, "message_dict"):

        for field_name, field_errors in exc.message_dict.items():

            label = field_name.replace("_", " ").title()

            for error in field_errors:
                messages.error(
                    request,
                    f"{label}: {error}"
                )

        return

    for error in exc.messages:
        messages.error(request, error)


VALID_SUBMIT_ACTIONS = {
    "draft",
    "finalize",
}


def get_submit_action(request):

    action = (
        request.POST
        .get("submit_action", "")
        .strip()
        .lower()
    )

    if action not in VALID_SUBMIT_ACTIONS:
        raise ValidationError(
            "Invalid Builty action. Please reopen the modal and try again."
        )

    return action


def prepare_finalized_update_data(request, builty):

    data = request.POST.copy()
    changed_fields = []

    submitted_customer = data.get("customer")

    if submitted_customer not in (None, ""):

        if str(submitted_customer) != str(builty.customer_id):
            changed_fields.append("Customer")

    submitted_date = data.get("builty_date")
    original_date = builty.builty_date.isoformat()

    if submitted_date not in (
        None,
        "",
        original_date,
    ):
        changed_fields.append("Builty Date")

    financial_fields = (
        (
            "freight_amount",
            "Freight Amount",
            builty.freight_amount,
        ),
        (
            "advance_amount",
            "Advance Amount",
            builty.advance_amount,
        ),
    )

    for field_name, label, original_value in financial_fields:

        submitted_value = data.get(field_name)

        if submitted_value in (None, ""):
            continue

        try:
            submitted_decimal = Decimal(submitted_value)

        except Exception:
            changed_fields.append(label)

        else:
            if submitted_decimal != Decimal(
                original_value or 0
            ):
                changed_fields.append(label)

    if changed_fields:
        raise ValidationError(
            "Finalized Builty financial fields cannot be edited: "
            + ", ".join(changed_fields)
            + "."
        )

    # Disabled fields browser POST nahi karta,
    # isliye original values restore ho rahi hain.
    data["customer"] = str(builty.customer_id)
    data["builty_date"] = original_date
    data["freight_amount"] = str(
        builty.freight_amount
    )
    data["advance_amount"] = str(
        builty.advance_amount
    )

    return data

def update_customer_balances(
    *,
    old_customer_id=None,
    old_contribution=Decimal("0.00"),
    new_customer_id=None,
    new_contribution=Decimal("0.00"),
):
    customer_ids = {
        customer_id
        for customer_id in (old_customer_id, new_customer_id)
        if customer_id
    }

    locked_customers = {
        customer.pk: customer
        for customer in (
            Customer.objects
            .select_for_update()
            .filter(pk__in=sorted(customer_ids))
        )
    }

    old_contribution = Decimal(old_contribution or 0)
    new_contribution = Decimal(new_contribution or 0)

    if old_customer_id and old_customer_id == new_customer_id:
        customer = locked_customers[old_customer_id]
        customer.current_balance = Decimal(customer.current_balance or 0) + (
            new_contribution - old_contribution
        )
        customer.save(update_fields=["current_balance"])
        return

    if old_customer_id:
        old_customer = locked_customers[old_customer_id]
        old_customer.current_balance = Decimal(
            old_customer.current_balance or 0
        ) - old_contribution
        old_customer.save(update_fields=["current_balance"])

    if new_customer_id:
        new_customer = locked_customers[new_customer_id]
        new_customer.current_balance = Decimal(
            new_customer.current_balance or 0
        ) + new_contribution
        new_customer.save(update_fields=["current_balance"])


class BuiltyListView(LoginRequiredMixin, ListView):
    model = Builty
    template_name = "operations/builty_lr.html"
    context_object_name = "builties"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Builty.objects
            .select_related("customer", "vehicle", "driver")
            .order_by("-builty_date", "-created_at")
        )

        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(builty_no__icontains=search)
                | Q(customer__company_name__icontains=search)
                | Q(origin_city__icontains=search)
                | Q(destination_city__icontains=search)
                | Q(vehicle_number__icontains=search)
                | Q(driver_name__icontains=search)
            )

        document_status = self.request.GET.get("document_status", "").strip()
        if document_status:
            queryset = queryset.filter(document_status=document_status)

        filter_type = self.request.GET.get("filter", "").strip()
        today = timezone.localdate()

        if filter_type == "today":
            queryset = queryset.filter(builty_date=today)
        elif filter_type == "yesterday":
            queryset = queryset.filter(
                builty_date=today - timedelta(days=1)
            )
        elif filter_type == "week":
            queryset = queryset.filter(
                builty_date__gte=today - timedelta(days=7)
            )
        elif filter_type == "month":
            queryset = queryset.filter(
                builty_date__year=today.year,
                builty_date__month=today.month,
            )
        elif filter_type == "range":
            start = self.request.GET.get("start_date", "").strip()
            end = self.request.GET.get("end_date", "").strip()

            if start:
                queryset = queryset.filter(builty_date__gte=start)
            if end:
                queryset = queryset.filter(builty_date__lte=end)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stats = Builty.objects.aggregate(
            total=Count("id"),
            drafts=Count("id", filter=Q(document_status="draft")),
            pending=Count(
                "id",
                filter=Q(
                    document_status="finalized",
                    dispatch_status="pending",
                ),
            ),
            transit=Count(
                "id",
                filter=Q(dispatch_status="transit"),
            ),
        )

        context["stats"] = stats
        return context


class BuiltyCreateView(LoginRequiredMixin, View):

    def get(self, request):
        return redirect(
            "builty:builty_list"
        )

    def post(self, request):

        try:
            submit_action = get_submit_action(
                request
            )

        except ValidationError as exc:

            add_validation_errors_to_messages(
                request,
                exc
            )

            return redirect(
                f"{reverse('builty:builty_list')}?open_builty=1"
            )

        should_finalize = (
            submit_action == "finalize"
        )

        # Hamesha pehle Draft save hogi.
        # Finalize service financial posting karegi.
        instance = Builty(
            document_status="draft"
        )

        form = BuiltyForm(
            request.POST,
            instance=instance
        )

        if not form.is_valid():

            add_form_errors_to_messages(
                request,
                form
            )

            return redirect(
                f"{reverse('builty:builty_list')}?open_builty=1"
            )

        try:

            with transaction.atomic():

                builty = form.save(
                    commit=False
                )

                builty.document_status = "draft"
                builty.finalized_at = None

                if not builty.vehicle_id:
                    builty.vehicle_number = None

                if not builty.driver_id:
                    builty.driver_name = None
                    builty.driver_phone = None

                builty.full_clean()
                builty.save()

                if should_finalize:

                    builty, payment, _ = (
                        finalize_builty(
                            builty_id=builty.pk
                        )
                    )

                    payment_message = (
                        (
                            f" Advance payment "
                            f"{payment.payment_id} was also recorded."
                        )
                        if payment
                        else ""
                    )

                    messages.success(
                        request,
                        (
                            f"Builty {builty.builty_no} "
                            f"finalized successfully."
                            f"{payment_message}"
                        )
                    )

                else:

                    messages.success(
                        request,
                        (
                            f"Builty {builty.builty_no} "
                            "saved as Draft."
                        )
                    )

        except ValidationError as exc:

            add_validation_errors_to_messages(
                request,
                exc
            )

        except Exception:

            logger.exception(
                "Unable to create Builty."
            )

            messages.error(
                request,
                "Unable to create Builty."
            )

        return redirect(
            "builty:builty_list"
        )


class BuiltyUpdateView(LoginRequiredMixin, View):

    def post(self, request, pk):

        try:
            submit_action = get_submit_action(
                request
            )

        except ValidationError as exc:

            add_validation_errors_to_messages(
                request,
                exc
            )

            return redirect(
                "builty:builty_list"
            )

        try:

            with transaction.atomic():
                builty = (
                    Builty.objects
                    .select_for_update()
                    .get(pk=pk)
                )

                if not builty.is_editable:

                    raise ValidationError(
                        "Only pending, non-cancelled Builties can be edited."
                    )

                was_draft = (
                    builty.document_status
                    == "draft"
                )

                # Draft mein original POST.
                # Finalized mein financial values locked.
                if was_draft:
                    form_data = request.POST

                else:
                    form_data = (
                        prepare_finalized_update_data(
                            request,
                            builty
                        )
                    )

                form = BuiltyForm(
                    form_data,
                    instance=builty,
                    lock_financial_fields=not was_draft,
                )

                if not form.is_valid():

                    add_form_errors_to_messages(
                        request,
                        form
                    )

                    return redirect(
                        "builty:builty_list"
                    )

                updated = form.save(
                    commit=False
                )

                updated.document_status = (
                    "draft"
                    if was_draft
                    else "finalized"
                )

                if not updated.vehicle_id:
                    updated.vehicle_number = None

                if not updated.driver_id:
                    updated.driver_name = None
                    updated.driver_phone = None

                # Finalized operational update:
                # selected driver/vehicle lock karo.
                if not was_draft:

                    if updated.vehicle_id:

                        updated.vehicle = (
                            Vehicle.objects
                            .select_for_update()
                            .get(
                                pk=updated.vehicle_id
                            )
                        )

                    if updated.driver_id:

                        updated.driver = (
                            Driver.objects
                            .select_for_update()
                            .get(
                                pk=updated.driver_id
                            )
                        )

                updated.full_clean()
                updated.save()

                if not was_draft:
                    from trips.services import sync_pending_trip_from_builty
                    sync_pending_trip_from_builty(
                        builty_id=updated.pk,
                    )

                # Draft ko Finalize kiya gaya.
                if (
                    was_draft
                    and submit_action == "finalize"
                ):

                    updated, payment, _ = (
                        finalize_builty(
                            builty_id=updated.pk
                        )
                    )

                    payment_message = (
                        (
                            f" Advance payment "
                            f"{payment.payment_id} was also recorded."
                        )
                        if payment
                        else ""
                    )

                    messages.success(
                        request,
                        (
                            f"Builty {updated.builty_no} "
                            f"finalized successfully."
                            f"{payment_message}"
                        )
                    )

                else:

                    messages.success(
                        request,
                        (
                            f"Builty {updated.builty_no} "
                            "updated successfully."
                        )
                    )

        except Builty.DoesNotExist:

            messages.error(
                request,
                "Builty not found."
            )

        except ValidationError as exc:

            add_validation_errors_to_messages(
                request,
                exc
            )

        except Exception:

            logger.exception(
                "Unable to update Builty."
            )

            messages.error(
                request,
                "Unable to update Builty."
            )

        return redirect(
            "builty:builty_list"
        )


class BuiltyCancelView(LoginRequiredMixin, View):

    def post(self, request, pk):
        reason = request.POST.get("cancel_reason", "").strip()

        if not reason:
            messages.error(request, "Cancellation reason is required.")
            return redirect("builty:builty_list")

        try:
            with transaction.atomic():
                builty = (
                    Builty.objects
                    .select_for_update()
                    .select_related("customer")
                    .get(pk=pk)
                )

                if builty.document_status == "cancelled":
                    messages.warning(request, "Builty is already cancelled.")
                    return redirect("builty:builty_list")

                if builty.dispatch_status != "pending":
                    messages.error(
                        request,
                        "A dispatched Builty cannot be cancelled from this screen.",
                    )
                    return redirect("builty:builty_list")

                if builty.payments.exists():
                    messages.error(
                        request,
                        (
                            "Builty cannot be cancelled because payments are "
                            "already recorded against it."
                        ),
                    )
                    return redirect("builty:builty_list")

                if builty.document_status == "finalized":
                    update_customer_balances(
                        old_customer_id=builty.customer_id,
                        old_contribution=builty.remaining_amount,
                    )

                builty.document_status = "cancelled"
                builty.cancel_reason = reason
                builty.cancelled_at = timezone.now()
                builty.save(
                    update_fields=[
                        "document_status",
                        "cancel_reason",
                        "cancelled_at",
                        "updated_at",
                    ]
                )

                messages.success(
                    request,
                    f"Builty {builty.builty_no} cancelled successfully.",
                )

        except Builty.DoesNotExist:
            messages.error(request, "Builty not found.")

        except Exception:
            logger.exception("Unable to cancel Builty.")
            messages.error(request, "Unable to cancel Builty.")

        return redirect("builty:builty_list")


class BuiltyDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
        builty = get_object_or_404(
            Builty.objects.select_related("customer", "vehicle", "driver"),
            pk=pk,
        )

        builty_date = date_payload(builty.builty_date)

        return JsonResponse({
            "id": builty.pk,
            "builty_no": builty.builty_no,
            "builty_date": builty_date["value"],
            "builty_date_display": builty_date["display"],
            "document_status": builty.document_status,
            "document_status_display": builty.get_document_status_display(),
            "dispatch_status": builty.dispatch_status,
            "dispatch_status_display": builty.get_dispatch_status_display(),
            "payment_status": builty.payment_status,
            "payment_status_display": builty.get_payment_status_display(),
            "customer_id": builty.customer_id,
            "customer_name": builty.customer.company_name,
            "customer_phone": builty.customer.phone or "",
            "customer_cnic": builty.customer.cnic_ntn or "",
            "receiver_name": builty.receiver_name or "",
            "receiver_phone": builty.receiver_phone or "",
            "origin_city": builty.origin_city or "",
            "destination_city": builty.destination_city or "",
            "route": builty.route,
            "goods_description": builty.goods_description or "",
            "weight": decimal_string(builty.weight),
            "package_count": builty.package_count or "",
            "freight_amount": decimal_string(builty.freight_amount),
            "advance_amount": decimal_string(builty.advance_amount),
            "remaining_amount": decimal_string(builty.remaining_amount),
            "vehicle_id": builty.vehicle_id or "",
            "vehicle_number": builty.vehicle_number or "",
            "vehicle_label": (
                f"{builty.vehicle.registration_number} • "
                f"{builty.vehicle.get_vehicle_type_display()}"
                if builty.vehicle_id
                else ""
            ),
            "driver_id": builty.driver_id or "",
            "driver_name": builty.driver_name or "",
            "driver_phone": builty.driver_phone or "",
            "driver_label": (
                f"{builty.driver.full_name} • {builty.driver.phone}"
                if builty.driver_id
                else ""
            ),
            "notes": builty.notes or "",
            "cancel_reason": builty.cancel_reason or "",
            "is_editable": builty.is_editable,
            "financial_fields_editable": (builty.financial_fields_editable),
            "update_url": reverse(
                "builty:builty_update",
                args=[builty.pk],
            ),
            "cancel_url": reverse(
                "builty:builty_cancel",
                args=[builty.pk],
            ),
            "created_at": timezone.localtime(
                builty.created_at
            ).strftime("%d %b %Y %I:%M %p"),
            "updated_at": timezone.localtime(
                builty.updated_at
            ).strftime("%d %b %Y %I:%M %p"),
        })


class CustomerSearchView(LoginRequiredMixin, View):

    def get(self, request):
        query = request.GET.get("q", "").strip()

        if not query:
            return JsonResponse([], safe=False)

        customers = (
            Customer.objects
            .filter(
                Q(company_name__icontains=query)
                | Q(phone__icontains=query)
                | Q(cnic_ntn__icontains=query)
            )
            .only("id", "company_name", "phone", "cnic_ntn")[:10]
        )

        return JsonResponse([
            {
                "id": customer.id,
                "label": customer.company_name,
                "secondary": customer.phone or "",
                "company_name": customer.company_name,
                "phone": customer.phone or "",
                "cnic": customer.cnic_ntn or "",
            }
            for customer in customers
        ], safe=False)


class VehicleSearchView(LoginRequiredMixin, View):

    def get(self, request):
        query = request.GET.get("q", "").strip()

        if not query:
            return JsonResponse([], safe=False)

        current_builty_id = request.GET.get("builty_id")

        busy_vehicle_ids = (
            Builty.objects
            .filter(
                document_status="finalized",
                dispatch_status__in=("pending", "transit"),
            )
            .exclude(pk=current_builty_id if current_builty_id else None)
            .exclude(vehicle_id__isnull=True)
            .values_list("vehicle_id", flat=True)
        )

        vehicles = (
            Vehicle.objects
            .filter(status="available")
            .exclude(pk__in=busy_vehicle_ids)
            .filter(
                Q(registration_number__icontains=query)
                | Q(vehicle_code__icontains=query)
                | Q(make__icontains=query)
                | Q(model__icontains=query)
            )
            .order_by("registration_number")[:10]
        )

        return JsonResponse([
            {
                "id": vehicle.id,
                "label": vehicle.registration_number,
                "secondary": (
                    f"{vehicle.get_vehicle_type_display()}"
                    + (f" • {vehicle.capacity_tons} Tons" if vehicle.capacity_tons else "")
                ),
                "registration_number": vehicle.registration_number,
            }
            for vehicle in vehicles
        ], safe=False)


class DriverSearchView(LoginRequiredMixin, View):

    def get(self, request):
        query = request.GET.get("q", "").strip()

        if not query:
            return JsonResponse([], safe=False)

        current_builty_id = request.GET.get("builty_id")

        busy_driver_ids = (
            Builty.objects
            .filter(
                document_status="finalized",
                dispatch_status__in=("pending", "transit"),
            )
            .exclude(pk=current_builty_id if current_builty_id else None)
            .exclude(driver_id__isnull=True)
            .values_list("driver_id", flat=True)
        )

        drivers = (
            Driver.objects
            .filter(
                status="active",
                license_expiry_date__gte=timezone.localdate(),
            )
            .exclude(pk__in=busy_driver_ids)
            .filter(
                Q(full_name__icontains=query)
                | Q(driver_code__icontains=query)
                | Q(phone__icontains=query)
                | Q(cnic__icontains=query)
                | Q(license_number__icontains=query)
            )
            .order_by("full_name")[:10]
        )

        return JsonResponse([
            {
                "id": driver.id,
                "label": driver.full_name,
                "secondary": f"{driver.phone} • {driver.get_license_type_display()}",
                "full_name": driver.full_name,
                "phone": driver.phone,
            }
            for driver in drivers
        ], safe=False)
