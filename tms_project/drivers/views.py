from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView

from .forms import DriverForm
from .models import Driver


def add_form_errors_to_messages(request, form):
    """
    Generic 'Unable to create' ki jagah exact field error show karega.
    """

    for field_name, errors in form.errors.items():

        if field_name == "__all__":
            field_label = "Error"
        else:
            field_label = form.fields[field_name].label or field_name

        for error in errors:
            messages.error(
                request,
                f"{field_label}: {error}"
            )


class DriverListView(LoginRequiredMixin, ListView):
    model = Driver
    template_name = "drivers/drivers.html"
    context_object_name = "drivers"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Driver.objects
            .all()
            .order_by("-created_at")
        )

        search = self.request.GET.get(
            "search",
            ""
        ).strip()

        if search:
            queryset = queryset.filter(
                Q(driver_code__icontains=search)
                | Q(full_name__icontains=search)
                | Q(cnic__icontains=search)
                | Q(phone__icontains=search)
                | Q(license_number__icontains=search)
                | Q(city__icontains=search)
            )

        return queryset


class DriverCreateView(LoginRequiredMixin, View):

    def post(self, request):

        form = DriverForm(request.POST)

        if not form.is_valid():
            add_form_errors_to_messages(request, form)
            return redirect("drivers:drivers_view")

        try:
            with transaction.atomic():

                driver = form.save()

                messages.success(
                    request,
                    f"Driver {driver.driver_code} created successfully."
                )

        except IntegrityError:
            messages.error(
                request,
                "Duplicate CNIC, license number, or driver code found."
            )

        except Exception as error:
            messages.error(
                request,
                f"Unable to create driver. Error: {error}"
            )

        return redirect("drivers:drivers_view")


class DriverUpdateView(LoginRequiredMixin, View):

    def post(self, request, pk):

        try:
            driver = Driver.objects.get(pk=pk)

        except Driver.DoesNotExist:
            messages.error(
                request,
                "Driver not found."
            )
            return redirect("drivers:drivers_view")

        form = DriverForm(
            request.POST,
            instance=driver
        )

        if not form.is_valid():
            add_form_errors_to_messages(request, form)
            return redirect("drivers:drivers_view")

        try:
            with transaction.atomic():

                driver = form.save()

                messages.success(
                    request,
                    f"Driver {driver.driver_code} updated successfully."
                )

        except IntegrityError:
            messages.error(
                request,
                "Duplicate CNIC or license number found."
            )

        except Exception as error:
            messages.error(
                request,
                f"Unable to update driver. Error: {error}"
            )

        return redirect("drivers:drivers_view")


class DriverDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk):

        try:
            driver = Driver.objects.get(pk=pk)

        except Driver.DoesNotExist:
            messages.error(
                request,
                "Driver not found."
            )
            return redirect("drivers:drivers_view")

        try:
            driver_name = driver.full_name
            driver.delete()

            messages.success(
                request,
                f"Driver {driver_name} deleted successfully."
            )

        except ProtectedError:
            driver.status = "inactive"
            driver.save(update_fields=["status"])

            messages.warning(
                request,
                "This driver is linked with records, so it was marked inactive instead of deleting."
            )

        except Exception as error:
            messages.error(
                request,
                f"Unable to delete driver. Error: {error}"
            )

        return redirect("drivers:drivers_view")