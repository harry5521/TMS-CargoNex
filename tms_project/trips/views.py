import logging
from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from builty.models import Builty

from .forms import (
    TripAssignForm,
    TripExpenseCreateForm,
    TripExpenseTitleForm,
)
from .models import Trip
from .services import (
    complete_trip,
    create_trip_expense,
    ensure_trip_for_builty,
    start_trip,
    update_trip_expense_title,
)


logger = logging.getLogger(__name__)


def add_validation_messages(request, exc):
    if hasattr(exc, "message_dict"):
        for field, errors in exc.message_dict.items():
            label = field.replace("_", " ").title()
            for error in errors:
                messages.error(request, f"{label}: {error}")
        return

    for error in exc.messages:
        messages.error(request, error)


def money_string(value):
    return str(value if value is not None else Decimal("0.00"))


def datetime_display(value):
    if not value:
        return "—"
    return timezone.localtime(value).strftime("%d %b %Y %I:%M %p")


class TripListView(ListView):
    model = Trip
    template_name = "operations/trips_dispatch.html"
    context_object_name = "trips"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Trip.objects
            .select_related(
                "builty",
                "builty__customer",
                "driver",
                "vehicle",
            )
            .annotate(
                expense_total=Coalesce(
                    Sum("expenses__amount"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .order_by("-scheduled_date", "-created_at")
        )

        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(trip_no__icontains=search)
                | Q(builty__builty_no__icontains=search)
                | Q(builty__customer__company_name__icontains=search)
                | Q(builty__origin_city__icontains=search)
                | Q(builty__destination_city__icontains=search)
                | Q(driver__full_name__icontains=search)
                | Q(vehicle__registration_number__icontains=search)
            )

        status = self.request.GET.get("status", "").strip()
        if status:
            queryset = queryset.filter(status=status)

        date_from = self.request.GET.get("date_from", "").strip()
        date_to = self.request.GET.get("date_to", "").strip()

        if date_from:
            queryset = queryset.filter(scheduled_date__gte=date_from)

        if date_to:
            queryset = queryset.filter(scheduled_date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stats = Trip.objects.aggregate(
            total=Count("id", distinct=True),
            pending=Count(
                "id",
                filter=Q(status="pending"),
                distinct=True,
            ),
            in_transit=Count(
                "id",
                filter=Q(status="in_transit"),
                distinct=True,
            ),
            completed=Count(
                "id",
                filter=Q(status="completed"),
                distinct=True,
            ),
        )

        stats["total_expenses"] = (
            Trip.objects.aggregate(
                total=Coalesce(
                    Sum("expenses__amount"),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(
                        max_digits=12,
                        decimal_places=2,
                    ),
                )
            )["total"]
        )

        current_trips = (
            Trip.objects
            .filter(status="pending")
            .select_related(
                "builty",
                "builty__customer",
                "driver",
                "vehicle",
            )
            .order_by("scheduled_date", "created_at")[:10]
        )

        context["stats"] = stats
        context["current_trips"] = current_trips
        context["current_trip_count"] = Trip.objects.filter(status="pending").count()
        context["open_expenses_trip_id"] = self.request.GET.get(
            "open_expenses", ""
        )
        return context


class TripAssignView(View):
    def post(self, request):
        form = TripAssignForm(request.POST)

        if not form.is_valid():
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
            return redirect("trips:trip_list")

        try:
            trip = ensure_trip_for_builty(
                builty_id=form.cleaned_data["builty_id"]
            )
            messages.success(
                request,
                f"Trip {trip.trip_no} assigned successfully.",
            )
        except ValidationError as exc:
            add_validation_messages(request, exc)
        except Exception:
            logger.exception("Unable to assign Trip.")
            messages.error(request, "Unable to assign Trip.")

        return redirect("trips:trip_list")


class TripStartView(View):
    def post(self, request, pk):
        try:
            trip = start_trip(trip_id=pk)
            messages.success(request, f"Trip {trip.trip_no} started successfully.")
        except ValidationError as exc:
            add_validation_messages(request, exc)
        except Exception:
            logger.exception("Unable to start Trip.")
            messages.error(request, "Unable to start Trip.")

        return redirect("trips:trip_list")


class TripCompleteView(View):
    def post(self, request, pk):
        try:
            trip = complete_trip(trip_id=pk)
            messages.success(
                request,
                f"Trip {trip.trip_no} completed successfully.",
            )
        except ValidationError as exc:
            add_validation_messages(request, exc)
        except Exception:
            logger.exception("Unable to complete Trip.")
            messages.error(request, "Unable to complete Trip.")

        return redirect("trips:trip_list")


class TripDetailView(View):
    def get(self, request, pk):
        trip = get_object_or_404(
            Trip.objects.select_related(
                "builty",
                "builty__customer",
                "driver",
                "vehicle",
            ).prefetch_related("expenses"),
            pk=pk,
        )

        builty = trip.builty

        expenses = [
            {
                "id": expense.pk,
                "expense_no": expense.expense_no,
                "title": expense.title,
                "amount": money_string(expense.amount),
                "payment_mode": expense.payment_mode,
                "payment_mode_display": expense.get_payment_mode_display(),
                "reference_no": expense.reference_no or "",
                "expense_date": expense.expense_date.isoformat(),
                "expense_date_display": expense.expense_date.strftime("%d %b %Y"),
                "remarks": expense.remarks or "",
                "update_title_url": reverse(
                    "trips:expense_update_title",
                    args=[expense.pk],
                ),
            }
            for expense in trip.expenses.all()
        ]

        return JsonResponse({
            "id": trip.pk,
            "trip_no": trip.trip_no,
            "status": trip.status,
            "status_display": trip.get_status_display(),
            "scheduled_date": trip.scheduled_date.isoformat(),
            "scheduled_date_display": trip.scheduled_date.strftime("%d %b %Y"),
            "started_at_display": datetime_display(trip.started_at),
            "completed_at_display": datetime_display(trip.completed_at),
            "notes": trip.notes or "",
            "can_start": trip.can_start,
            "can_complete": trip.can_complete,
            "start_url": reverse("trips:trip_start", args=[trip.pk]),
            "complete_url": reverse("trips:trip_complete", args=[trip.pk]),
            "expense_create_url": reverse(
                "trips:expense_create",
                args=[trip.pk],
            ),
            "total_expenses": money_string(trip.total_expenses),
            "vehicle": {
                "id": trip.vehicle_id,
                "registration_number": trip.vehicle.registration_number,
                "vehicle_code": trip.vehicle.vehicle_code,
                "type": trip.vehicle.get_vehicle_type_display(),
                "capacity": (
                    money_string(trip.vehicle.capacity_tons)
                    if trip.vehicle.capacity_tons
                    else ""
                ),
            },
            "driver": {
                "id": trip.driver_id,
                "driver_code": trip.driver.driver_code,
                "name": trip.driver.full_name,
                "phone": trip.driver.phone,
                "cnic": trip.driver.cnic,
                "license_number": trip.driver.license_number,
            },
            "builty": {
                "id": builty.pk,
                "builty_no": builty.builty_no,
                "date": builty.builty_date.isoformat(),
                "date_display": builty.builty_date.strftime("%d %b %Y"),
                "customer": builty.customer.company_name,
                "customer_phone": builty.customer.phone or "",
                "receiver_name": builty.receiver_name,
                "receiver_phone": builty.receiver_phone or "",
                "origin_city": builty.origin_city,
                "destination_city": builty.destination_city,
                "route": builty.route,
                "goods_description": builty.goods_description,
                "weight": money_string(builty.weight),
                "package_count": builty.package_count or "",
                "freight_amount": money_string(builty.freight_amount),
                "advance_amount": money_string(builty.advance_amount),
                "remaining_amount": money_string(builty.remaining_amount),
                "payment_status": builty.get_payment_status_display(),
                "dispatch_status": builty.get_dispatch_status_display(),
                "notes": builty.notes or "",
            },
            "expenses": expenses,
        })


class UnassignedBuiltySearchView(View):
    def get(self, request):
        query = request.GET.get("q", "").strip()

        if not query:
            return JsonResponse([], safe=False)

        builties = (
            Builty.objects
            .filter(
                document_status="finalized",
                dispatch_status="pending",
                trip__isnull=True,
                driver__isnull=False,
                vehicle__isnull=False,
            )
            .select_related("customer", "driver", "vehicle")
            .filter(
                Q(builty_no__icontains=query)
                | Q(customer__company_name__icontains=query)
                | Q(origin_city__icontains=query)
                | Q(destination_city__icontains=query)
                | Q(driver__full_name__icontains=query)
                | Q(vehicle__registration_number__icontains=query)
            )
            .order_by("-builty_date", "-created_at")[:10]
        )

        return JsonResponse([
            {
                "id": builty.pk,
                "builty_no": builty.builty_no,
                "customer": builty.customer.company_name,
                "route": builty.route,
                "driver": builty.driver.full_name,
                "vehicle": builty.vehicle.registration_number,
            }
            for builty in builties
        ], safe=False)


class TripExpenseCreateView(View):
    def post(self, request, trip_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        form = TripExpenseCreateForm(request.POST)

        if not form.is_valid():
            for field, errors in form.errors.items():
                label = form.fields[field].label or field.replace("_", " ").title()
                for error in errors:
                    messages.error(request, f"{label}: {error}")
            return redirect(
                f"{reverse('trips:trip_list')}?search={trip.trip_no}"
                f"&open_expenses={trip.pk}"
            )

        try:
            expense, _ = create_trip_expense(
                trip_id=trip.pk,
                cleaned_data=form.cleaned_data,
            )
            messages.success(
                request,
                f"Expense {expense.expense_no} recorded successfully.",
            )
        except ValidationError as exc:
            add_validation_messages(request, exc)
        except Exception:
            logger.exception("Unable to create Trip expense.")
            messages.error(request, "Unable to create Trip expense.")

        return redirect(
            f"{reverse('trips:trip_list')}?search={trip.trip_no}"
            f"&open_expenses={trip.pk}"
        )


class TripExpenseTitleUpdateView(View):
    def post(self, request, pk):
        form = TripExpenseTitleForm(request.POST)

        if not form.is_valid():
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
            return redirect("trips:trip_list")

        try:
            expense = update_trip_expense_title(
                expense_id=pk,
                title=form.cleaned_data["title"],
            )
            messages.success(
                request,
                f"Expense {expense.expense_no} title updated successfully.",
            )
            trip = expense.trip
        except ValidationError as exc:
            add_validation_messages(request, exc)
            return redirect("trips:trip_list")
        except Exception:
            logger.exception("Unable to update Trip expense title.")
            messages.error(request, "Unable to update Trip expense title.")
            return redirect("trips:trip_list")

        return redirect(
            f"{reverse('trips:trip_list')}?search={trip.trip_no}"
            f"&open_expenses={trip.pk}"
        )
