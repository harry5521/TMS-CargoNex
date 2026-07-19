import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from customers.models import Customer


class Builty(models.Model):

    PAYMENT_STATUS = (
        ("paid", "Paid"),
        ("partial", "Partial"),
        ("topay", "To Pay"),
    )

    DISPATCH_STATUS = (
        ("pending", "Pending Dispatch"),
        ("transit", "In Transit"),
        ("completed", "Completed"),
    )

    DOCUMENT_STATUS = (
        ("draft", "Draft"),
        ("finalized", "Finalized"),
        ("cancelled", "Cancelled"),
    )

    FINANCIAL_LOCKED_FIELDS = (
        "customer_id",
        "builty_date",
        "freight_amount",
        "advance_amount",
    )

    # =========================
    # BASIC INFO
    # =========================

    builty_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        editable=False,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="builties",
    )

    builty_date = models.DateField(
        default=timezone.localdate,
    )

    document_status = models.CharField(
        max_length=15,
        choices=DOCUMENT_STATUS,
        default="draft",
        db_index=True,
    )

    finalized_at = models.DateTimeField(
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

    # =========================
    # CONSIGNEE
    # =========================

    receiver_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    receiver_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    # =========================
    # ROUTE
    # =========================

    origin_city = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    destination_city = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    # =========================
    # SHIPMENT
    # =========================

    goods_description = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    package_count = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    # =========================
    # FREIGHT
    # =========================

    freight_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    advance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    remaining_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default="topay",
    )

    # =========================
    # DISPATCH
    # =========================

    dispatch_status = models.CharField(
        max_length=15,
        choices=DISPATCH_STATUS,
        default="pending",
        db_index=True,
    )

    # =========================
    # VEHICLE & DRIVER
    # =========================

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.PROTECT,
        related_name="builties",
        null=True,
        blank=True,
    )

    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.PROTECT,
        related_name="builties",
        null=True,
        blank=True,
    )

    # Existing snapshot fields retained so old code and historical prints
    # continue working.
    vehicle_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    driver_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    driver_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    # =========================
    # NOTES / TIMESTAMPS
    # =========================

    notes = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-builty_date", "-created_at")
        indexes = [
            models.Index(fields=["document_status", "dispatch_status"]),
            models.Index(fields=["builty_date"]),
        ]

    @property
    def route(self):
        origin = self.origin_city or "—"
        destination = self.destination_city or "—"
        return f"{origin} → {destination}"

    @property
    def is_editable(self):
        return (
            self.document_status != "cancelled"
            and self.dispatch_status == "pending"
        )

    @property
    def financial_fields_editable(self):
        return self.document_status == "draft"

    @property
    def can_be_finalized(self):
        return (
            bool(self.customer_id)
            and bool(self.receiver_name.strip())
            and bool(self.origin_city.strip())
            and bool(self.destination_city.strip())
            and bool(self.goods_description.strip())
            and self.weight > 0
            and self.freight_amount > 0
            and bool(self.vehicle_id)
            and bool(self.driver_id)
        )

    def clean(self):
        errors = {}

        freight = Decimal(self.freight_amount or 0)
        advance = Decimal(self.advance_amount or 0)

        if advance > freight:
            errors["advance_amount"] = (
                "Advance amount cannot be greater than freight amount."
            )

        if (
            self.origin_city
            and self.destination_city
            and self.origin_city.strip().lower()
            == self.destination_city.strip().lower()
        ):
            errors["destination_city"] = (
                "Origin and destination cannot be the same."
            )

        if self.document_status == "finalized":
            required_values = {
                "receiver_name": self.receiver_name,
                "origin_city": self.origin_city,
                "destination_city": self.destination_city,
                "goods_description": self.goods_description,
            }

            for field_name, value in required_values.items():
                if not str(value or "").strip():
                    errors[field_name] = (
                        "This field is required to finalize Builty."
                    )

            if Decimal(self.weight or 0) <= 0:
                errors["weight"] = "Weight must be greater than zero."

            if freight <= 0:
                errors["freight_amount"] = (
                    "Freight amount must be greater than zero."
                )

            if not self.vehicle_id:
                errors["vehicle"] = (
                    "Vehicle is required to finalize Builty."
                )
            elif self.vehicle.status != "available":
                errors["vehicle"] = (
                    "Only an available vehicle can be assigned."
                )
            elif (
                type(self).objects
                .exclude(pk=self.pk)
                .filter(
                    vehicle_id=self.vehicle_id,
                    document_status="finalized",
                    dispatch_status__in=("pending", "transit"),
                )
                .exists()
            ):
                errors["vehicle"] = (
                    "Selected vehicle is already assigned to another active Builty."
                )

            if not self.driver_id:
                errors["driver"] = (
                    "Driver is required to finalize Builty."
                )
            else:
                if self.driver.status != "active":
                    errors["driver"] = (
                        "Only an active driver can be assigned."
                    )
                elif self.driver.license_expiry_date < timezone.localdate():
                    errors["driver"] = (
                        "Selected driver's licence has expired."
                    )
                elif (
                    type(self).objects
                    .exclude(pk=self.pk)
                    .filter(
                        driver_id=self.driver_id,
                        document_status="finalized",
                        dispatch_status__in=("pending", "transit"),
                    )
                    .exists()
                ):
                    errors["driver"] = (
                        "Selected driver is already assigned to another active Builty."
                    )

        if self.document_status == "cancelled" and not self.cancel_reason.strip():
            errors["cancel_reason"] = "Cancellation reason is required."

        if errors:
            raise ValidationError(errors)

    def _prevent_finalized_financial_changes(self):
        if self._state.adding or getattr(
            self,
            "_allow_financial_update",
            False,
        ):
            return

        previous = (
            type(self).objects
            .filter(pk=self.pk)
            .values(
                "document_status",
                "customer_id",
                "builty_date",
                "freight_amount",
                "advance_amount",
            )
            .first()
        )

        if not previous or previous["document_status"] != "finalized":
            return

        changed_labels = []

        if previous["customer_id"] != self.customer_id:
            changed_labels.append("Customer")

        if previous["builty_date"] != self.builty_date:
            changed_labels.append("Builty Date")

        if Decimal(previous["freight_amount"] or 0) != Decimal(
            self.freight_amount or 0
        ):
            changed_labels.append("Freight Amount")

        if Decimal(previous["advance_amount"] or 0) != Decimal(
            self.advance_amount or 0
        ):
            changed_labels.append("Advance Amount")

        if changed_labels:
            raise ValidationError(
                "Finalized Builty financial fields are locked: "
                + ", ".join(changed_labels)
                + ". Use an adjustment or payment workflow instead."
            )

    def save(self, *args, **kwargs):
        creating = self._state.adding

        self._prevent_finalized_financial_changes()

        self.receiver_name = (self.receiver_name or "").strip()
        self.origin_city = (self.origin_city or "").strip()
        self.destination_city = (self.destination_city or "").strip()
        self.goods_description = (self.goods_description or "").strip()
        self.notes = self.notes.strip() if self.notes else None

        freight = Decimal(self.freight_amount or 0)
        advance = Decimal(self.advance_amount or 0)

        self.remaining_amount = max(
            freight - advance,
            Decimal("0.00"),
        )

        if self.remaining_amount <= 0 and freight > 0:
            self.payment_status = "paid"
        elif advance > 0:
            self.payment_status = "partial"
        else:
            self.payment_status = "topay"

        if self.vehicle_id:
            self.vehicle_number = self.vehicle.registration_number

        if self.driver_id:
            self.driver_name = self.driver.full_name
            self.driver_phone = self.driver.phone

        if not self.builty_no:
            self.builty_no = f"TMP-{uuid.uuid4().hex[:12].upper()}"

        super().save(*args, **kwargs)

        if creating and self.builty_no.startswith("TMP-"):
            final_code = f"BLT-{self.pk + 1000}"

            if (
                type(self).objects
                .exclude(pk=self.pk)
                .filter(builty_no=final_code)
                .exists()
            ):
                final_code = f"BLT-{self.pk:06d}"

            type(self).objects.filter(pk=self.pk).update(
                builty_no=final_code
            )
            self.builty_no = final_code

    def __str__(self):
        return self.builty_no
