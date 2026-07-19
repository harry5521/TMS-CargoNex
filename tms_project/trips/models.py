import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone

from builty.models import Builty
from drivers.models import Driver
from vehicles.models import Vehicle


ACTIVE_TRIP_STATUSES = ("pending", "in_transit")


class Trip(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in_transit", "In Transit"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    trip_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        editable=False,
    )

    builty = models.OneToOneField(
        Builty,
        on_delete=models.PROTECT,
        related_name="trip",
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name="trips",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="trips",
    )

    scheduled_date = models.DateField(
        default=timezone.localdate,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancel_reason = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("-scheduled_date", "-created_at")
        indexes = [
            models.Index(fields=["status", "scheduled_date"]),
            models.Index(fields=["driver", "status"]),
            models.Index(fields=["vehicle", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["driver"],
                condition=Q(status__in=ACTIVE_TRIP_STATUSES),
                name="unique_active_trip_per_driver",
            ),
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=Q(status__in=ACTIVE_TRIP_STATUSES),
                name="unique_active_trip_per_vehicle",
            ),
        ]

    @property
    def route(self):
        return self.builty.route

    @property
    def total_expenses(self):
        return (
            self.expenses.aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

    @property
    def can_start(self):
        return (
            self.status == "pending"
            and self.builty.document_status == "finalized"
            and self.builty.dispatch_status == "pending"
        )

    @property
    def can_complete(self):
        return self.status == "in_transit"

    def clean(self):
        errors = {}

        if self.builty_id:
            if self.builty.document_status != "finalized":
                errors["builty"] = (
                    "Only a finalized Builty can be assigned to a Trip."
                )

            if self.builty.document_status == "cancelled":
                errors["builty"] = "A cancelled Builty cannot have a Trip."

        if self.status in ACTIVE_TRIP_STATUSES:
            if self.driver_id and (
                type(self).objects
                .exclude(pk=self.pk)
                .filter(
                    driver_id=self.driver_id,
                    status__in=ACTIVE_TRIP_STATUSES,
                )
                .exists()
            ):
                errors["driver"] = (
                    "Selected driver is already assigned to another active Trip."
                )

            if self.vehicle_id and (
                type(self).objects
                .exclude(pk=self.pk)
                .filter(
                    vehicle_id=self.vehicle_id,
                    status__in=ACTIVE_TRIP_STATUSES,
                )
                .exists()
            ):
                errors["vehicle"] = (
                    "Selected vehicle is already assigned to another active Trip."
                )

        if self.status == "in_transit" and not self.started_at:
            errors["started_at"] = "Started time is required for an active Trip."

        if self.status == "completed" and not self.completed_at:
            errors["completed_at"] = (
                "Completed time is required for a completed Trip."
            )

        if self.status == "cancelled" and not self.cancel_reason.strip():
            errors["cancel_reason"] = "Cancellation reason is required."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        creating = self._state.adding

        self.notes = self.notes.strip() if self.notes else None
        self.cancel_reason = (self.cancel_reason or "").strip()

        if not self.trip_no:
            self.trip_no = f"TMP-{uuid.uuid4().hex[:12].upper()}"

        super().save(*args, **kwargs)

        if creating and self.trip_no.startswith("TMP-"):
            final_code = f"TRP-{self.pk:06d}"
            type(self).objects.filter(pk=self.pk).update(trip_no=final_code)
            self.trip_no = final_code

    def __str__(self):
        return f"{self.trip_no} - {self.builty.builty_no}"


class TripExpense(models.Model):
    PAYMENT_MODES = (
        ("cash", "Cash"),
        ("bank", "Bank Transfer"),
        ("online", "Online Transfer"),
        ("cheque", "Cheque"),
    )

    expense_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        editable=False,
    )

    trip = models.ForeignKey(
        Trip,
        on_delete=models.PROTECT,
        related_name="expenses",
    )

    title = models.CharField(
        max_length=200,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODES,
        default="cash",
    )

    reference_no = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    expense_date = models.DateField(
        default=timezone.localdate,
        db_index=True,
    )

    remarks = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ("-expense_date", "-created_at")
        indexes = [
            models.Index(fields=["trip", "expense_date"]),
        ]

    def clean(self):
        errors = {}

        if not (self.title or "").strip():
            errors["title"] = "Expense title is required."

        if Decimal(self.amount or 0) <= 0:
            errors["amount"] = "Expense amount must be greater than zero."

        if self.payment_mode != "cash" and not (self.reference_no or "").strip():
            errors["reference_no"] = (
                "Reference number is required for non-cash expenses."
            )

        if self.trip_id and self.trip.status == "cancelled":
            errors["trip"] = "Expense cannot be added to a cancelled Trip."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        creating = self._state.adding

        self.title = (self.title or "").strip()
        self.reference_no = (
            self.reference_no.strip() if self.reference_no else None
        )
        self.remarks = self.remarks.strip() if self.remarks else None

        if not self.expense_no:
            self.expense_no = f"TMP-{uuid.uuid4().hex[:12].upper()}"

        super().save(*args, **kwargs)

        if creating and self.expense_no.startswith("TMP-"):
            final_code = f"EXP-{self.pk:06d}"
            type(self).objects.filter(pk=self.pk).update(expense_no=final_code)
            self.expense_no = final_code

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "Trip expenses cannot be deleted. Add a reversal entry instead."
        )

    def __str__(self):
        return f"{self.expense_no} - {self.title}"
