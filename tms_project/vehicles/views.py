import logging
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from .forms import VehicleForm
from .models import Vehicle


logger = logging.getLogger(__name__)


def add_form_errors_to_messages(request, form):

    for field_name, errors in form.errors.items():

        if field_name == "__all__":
            field_label = "Error"
        else:
            field_label = (
                form.fields[field_name].label
                or field_name.replace("_", " ").title()
            )

        for error in errors:
            messages.error(
                request,
                f"{field_label}: {error}"
            )


def date_data(value):

    if not value:
        return {
            "value": "",
            "display": "—",
        }

    return {
        "value": value.isoformat(),
        "display": value.strftime("%d %b %Y"),
    }


def decimal_string(value):

    if value is None:
        return None

    return str(value)


class VehicleListView(LoginRequiredMixin, ListView):

    model = Vehicle
    template_name = "vehicles/vehicles.html"
    context_object_name = "vehicles"
    paginate_by = 10

    def get_queryset(self):

        queryset = Vehicle.objects.all().order_by(
            "-created_at"
        )

        search = self.request.GET.get(
            "search",
            ""
        ).strip()

        if search:

            queryset = queryset.filter(
                Q(vehicle_code__icontains=search)
                | Q(registration_number__icontains=search)
                | Q(make__icontains=search)
                | Q(model__icontains=search)
                | Q(chassis_number__icontains=search)
                | Q(engine_number__icontains=search)
                | Q(owner_name__icontains=search)
            )

        return queryset


class VehicleCreateView(LoginRequiredMixin, View):

    def post(self, request):

        form = VehicleForm(request.POST)

        if not form.is_valid():

            add_form_errors_to_messages(
                request,
                form
            )

            return redirect(
                "vehicles:vehicles_view"
            )

        try:

            with transaction.atomic():

                vehicle = form.save()

                messages.success(
                    request,
                    (
                        f"Vehicle {vehicle.vehicle_code} "
                        "created successfully."
                    )
                )

        except IntegrityError:

            messages.error(
                request,
                (
                    "Duplicate registration, chassis "
                    "or engine number found."
                )
            )

        except Exception:

            logger.exception(
                "Unable to create vehicle."
            )

            messages.error(
                request,
                "Unable to create vehicle."
            )

        return redirect(
            "vehicles:vehicles_view"
        )


class VehicleUpdateView(LoginRequiredMixin, View):

    def post(self, request, pk):

        vehicle = get_object_or_404(
            Vehicle,
            pk=pk
        )

        form = VehicleForm(
            request.POST,
            instance=vehicle
        )

        if not form.is_valid():

            add_form_errors_to_messages(
                request,
                form
            )

            return redirect(
                "vehicles:vehicles_view"
            )

        try:

            with transaction.atomic():

                vehicle = form.save()

                messages.success(
                    request,
                    (
                        f"Vehicle {vehicle.vehicle_code} "
                        "updated successfully."
                    )
                )

        except IntegrityError:

            messages.error(
                request,
                (
                    "Duplicate registration, chassis "
                    "or engine number found."
                )
            )

        except Exception:

            logger.exception(
                "Unable to update vehicle."
            )

            messages.error(
                request,
                "Unable to update vehicle."
            )

        return redirect(
            "vehicles:vehicles_view"
        )


class VehicleDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk):

        vehicle = get_object_or_404(
            Vehicle,
            pk=pk
        )

        try:

            vehicle_name = (
                vehicle.registration_number
            )

            vehicle.delete()

            messages.success(
                request,
                (
                    f"Vehicle {vehicle_name} "
                    "deleted successfully."
                )
            )

        except ProtectedError:

            vehicle.status = "inactive"

            vehicle.save(
                update_fields=["status"]
            )

            messages.warning(
                request,
                (
                    "This vehicle is linked with other records, "
                    "so it was marked inactive instead of deleting."
                )
            )

        except Exception:

            logger.exception(
                "Unable to delete vehicle."
            )

            messages.error(
                request,
                "Unable to delete vehicle."
            )

        return redirect(
            "vehicles:vehicles_view"
        )


class VehicleDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):

        vehicle = get_object_or_404(
            Vehicle,
            pk=pk
        )

        purchase_date = date_data(
            vehicle.purchase_date
        )

        depreciation_start = date_data(
            vehicle.depreciation_start_date
        )

        disposal_date = date_data(
            vehicle.disposal_date
        )

        snapshot = (
            vehicle.depreciation_snapshot()
        )

        current_book_value = None

        if snapshot.get("applicable"):

            current_book_value = decimal_string(
                snapshot.get(
                    "current_book_value"
                )
            )

        return JsonResponse({
            "id": vehicle.pk,
            "vehicle_code": vehicle.vehicle_code,
            "registration_number": vehicle.registration_number,

            "vehicle_type": vehicle.vehicle_type,
            "vehicle_type_display": (
                vehicle.get_vehicle_type_display()
            ),

            "body_type": vehicle.body_type,
            "body_type_display": (
                vehicle.get_body_type_display()
            ),

            "make": vehicle.make or "",
            "model": vehicle.model or "",
            "model_year": vehicle.model_year or "",
            "color": vehicle.color or "",

            "chassis_number": (
                vehicle.chassis_number or ""
            ),

            "engine_number": (
                vehicle.engine_number or ""
            ),

            "capacity_tons": decimal_string(
                vehicle.capacity_tons
            ) or "",

            "ownership_type": (
                vehicle.ownership_type
            ),

            "ownership_type_display": (
                vehicle.get_ownership_type_display()
            ),

            "owner_name": vehicle.owner_name or "",
            "owner_phone": vehicle.owner_phone or "",

            "purchase_date": purchase_date["value"],
            "purchase_date_display": (
                purchase_date["display"]
            ),

            "purchase_cost": decimal_string(
                vehicle.purchase_cost
            ) or "",

            "depreciation_start_date": (
                depreciation_start["value"]
            ),

            "depreciation_start_date_display": (
                depreciation_start["display"]
            ),

            "residual_value": decimal_string(
                vehicle.residual_value
            ) or "0",

            "useful_life_years": (
                vehicle.useful_life_years
            ),

            "status": vehicle.status,
            "status_display": (
                vehicle.get_status_display()
            ),

            "disposal_date": disposal_date["value"],
            "disposal_date_display": (
                disposal_date["display"]
            ),

            "disposal_amount": decimal_string(
                vehicle.disposal_amount
            ) or "",

            "notes": vehicle.notes or "",

            "depreciation_applicable": (
                vehicle.depreciation_applicable
            ),

            "current_book_value": (
                current_book_value
            ),

            "created_at": timezone.localtime(
                vehicle.created_at
            ).strftime("%d %b %Y %I:%M %p"),

            "updated_at": timezone.localtime(
                vehicle.updated_at
            ).strftime("%d %b %Y %I:%M %p"),
        })


class VehicleDepreciationView(LoginRequiredMixin, View):

    def get(self, request, pk):

        vehicle = get_object_or_404(
            Vehicle,
            pk=pk
        )

        snapshot = (
            vehicle.depreciation_snapshot()
        )

        data = {}

        for key, value in snapshot.items():

            if isinstance(value, Decimal):
                data[key] = str(value)

            elif isinstance(value, date):
                data[key] = value.isoformat()

            else:
                data[key] = value

        data["vehicle_code"] = (
            vehicle.vehicle_code
        )

        data["registration_number"] = (
            vehicle.registration_number
        )

        data["ownership_type"] = (
            vehicle.get_ownership_type_display()
        )

        if snapshot.get("applicable"):

            data["as_of_date_display"] = (
                snapshot["as_of_date"]
                .strftime("%d %b %Y")
            )

        return JsonResponse(data)
    