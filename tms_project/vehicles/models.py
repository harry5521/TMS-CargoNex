import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone


MONEY_PLACES = Decimal("0.01")


def money(value):
    """
    Decimal value ko PKR-style two decimal places tak round karta hai.
    """
    return Decimal(value or 0).quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP,
    )


class Vehicle(models.Model):

    OWNERSHIP_TYPES = (
        ("company_owned", "Company Owned"),
        ("attached", "Attached Vehicle"),
        ("market_hired", "Market / Hired Vehicle"),
    )

    VEHICLE_TYPES = (
        ("truck", "Truck"),
        ("trailer", "Trailer"),
        ("mazda", "Mazda"),
        ("pickup", "Pickup"),
        ("dumper", "Dumper"),
        ("tanker", "Tanker"),
        ("other", "Other"),
    )

    BODY_TYPES = (
        ("open", "Open Body"),
        ("container", "Container"),
        ("flatbed", "Flatbed"),
        ("tanker", "Tanker"),
        ("dumper", "Dumper"),
        ("refrigerated", "Refrigerated"),
        ("other", "Other"),
    )

    STATUS_CHOICES = (
        ("available", "Available"),
        ("on_trip", "On Trip"),
        ("maintenance", "Under Maintenance"),
        ("inactive", "Inactive"),
        ("sold", "Sold"),
    )

    DEPRECIATION_METHODS = (
        ("straight_line", "Straight Line"),
    )

    # -------------------------
    # System Information
    # -------------------------

    vehicle_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
    )

    registration_number = models.CharField(
        max_length=30,
        unique=True,
    )

    # -------------------------
    # Vehicle Information
    # -------------------------

    vehicle_type = models.CharField(
        max_length=30,
        choices=VEHICLE_TYPES,
        default="truck",
    )

    body_type = models.CharField(
        max_length=30,
        choices=BODY_TYPES,
        default="open",
    )

    make = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    model = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    model_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
    )

    color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    chassis_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )

    engine_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )

    capacity_tons = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ],
    )

    # -------------------------
    # Ownership Information
    # -------------------------

    ownership_type = models.CharField(
        max_length=30,
        choices=OWNERSHIP_TYPES,
        default="company_owned",
    )

    owner_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Required for attached or market vehicles.",
    )

    owner_phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    # -------------------------
    # Purchase / Depreciation
    # -------------------------

    purchase_date = models.DateField(
        blank=True,
        null=True,
    )

    purchase_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ],
    )

    depreciation_start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date vehicle became available for company use.",
    )

    residual_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ],
        help_text="Expected resale value after useful life.",
    )

    useful_life_years = models.PositiveSmallIntegerField(
        default=10,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(30),
        ],
        help_text="Expected remaining useful life.",
    )

    depreciation_method = models.CharField(
        max_length=30,
        choices=DEPRECIATION_METHODS,
        default="straight_line",
    )

    # -------------------------
    # Disposal / Sale
    # -------------------------

    disposal_date = models.DateField(
        blank=True,
        null=True,
    )

    disposal_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ],
    )

    # -------------------------
    # Status
    # -------------------------

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="available",
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

    # -------------------------
    # Validation
    # -------------------------

    def clean(self):
        errors = {}

        current_year = timezone.localdate().year

        if self.model_year:
            if self.model_year < 1950:
                errors["model_year"] = (
                    "Model year cannot be earlier than 1950."
                )

            elif self.model_year > current_year + 1:
                errors["model_year"] = (
                    "Model year cannot be more than one year in the future."
                )

        if self.ownership_type == "company_owned":

            if not self.purchase_date:
                errors["purchase_date"] = (
                    "Purchase date is required for a company-owned vehicle."
                )

            if not self.purchase_cost:
                errors["purchase_cost"] = (
                    "Purchase cost is required for a company-owned vehicle."
                )

            if not self.depreciation_start_date:
                errors["depreciation_start_date"] = (
                    "Depreciation start date is required for a company-owned vehicle."
                )

            if (
                self.purchase_date
                and self.depreciation_start_date
                and self.depreciation_start_date < self.purchase_date
            ):
                errors["depreciation_start_date"] = (
                    "Depreciation start date cannot be before purchase date."
                )

            if (
                self.purchase_cost is not None
                and self.residual_value is not None
                and self.residual_value >= self.purchase_cost
            ):
                errors["residual_value"] = (
                    "Expected resale value must be less than purchase cost."
                )

        else:

            if not self.owner_name:
                errors["owner_name"] = (
                    "Owner name is required for attached or hired vehicles."
                )

        if self.status == "sold":

            if not self.disposal_date:
                errors["disposal_date"] = (
                    "Sale/disposal date is required when vehicle status is Sold."
                )

            if self.disposal_amount is None:
                errors["disposal_amount"] = (
                    "Sale amount is required when vehicle status is Sold."
                )

        if (
            self.disposal_date
            and self.depreciation_start_date
            and self.disposal_date < self.depreciation_start_date
        ):
            errors["disposal_date"] = (
                "Disposal date cannot be before depreciation start date."
            )

        if errors:
            raise ValidationError(errors)

    # -------------------------
    # Save / Code Generation
    # -------------------------

    def save(self, *args, **kwargs):

        creating = self._state.adding

        self.registration_number = (
            self.registration_number.strip().upper()
        )

        if self.chassis_number:
            self.chassis_number = (
                self.chassis_number.strip().upper()
            )

        if self.engine_number:
            self.engine_number = (
                self.engine_number.strip().upper()
            )

        # Temporary code max_length=30 ke andar rahega
        if not self.vehicle_code:
            self.vehicle_code = (
                f"TMP-{uuid.uuid4().hex[:20].upper()}"
            )

        super().save(*args, **kwargs)

        if creating and self.vehicle_code.startswith("TMP-"):

            final_code = f"VEH-{self.pk:06d}"

            type(self).objects.filter(
                pk=self.pk
            ).update(
                vehicle_code=final_code
            )

            self.vehicle_code = final_code

    # -------------------------
    # Depreciation
    # -------------------------

    @property
    def depreciation_applicable(self):
        return (
            self.ownership_type == "company_owned"
            and self.purchase_cost is not None
            and self.depreciation_start_date is not None
            and self.useful_life_years
        )

    def depreciation_snapshot(self, as_of_date=None):
        """
        Straight-line depreciation ka complete snapshot return karta hai.
        UI modal aur reports dono isi function ko use karenge.
        """

        as_of_date = as_of_date or timezone.localdate()

        if not self.depreciation_applicable:
            return {
                "applicable": False,
                "message": (
                    "Depreciation is not applicable to attached "
                    "or market-hired vehicles."
                ),
            }

        calculation_date = as_of_date

        if (
            self.status == "sold"
            and self.disposal_date
            and self.disposal_date < calculation_date
        ):
            calculation_date = self.disposal_date

        purchase_cost = money(self.purchase_cost)
        residual_value = money(self.residual_value)

        depreciable_amount = money(
            max(
                purchase_cost - residual_value,
                Decimal("0.00"),
            )
        )

        total_months = self.useful_life_years * 12

        monthly_depreciation = money(
            depreciable_amount / Decimal(total_months)
        )

        annual_depreciation = money(
            depreciable_amount
            / Decimal(self.useful_life_years)
        )

        start_date = self.depreciation_start_date

        if calculation_date < start_date:
            elapsed_months = 0

        else:
            elapsed_months = (
                (calculation_date.year - start_date.year) * 12
                + calculation_date.month
                - start_date.month
            )

            if calculation_date.day < start_date.day:
                elapsed_months -= 1

            elapsed_months = max(elapsed_months, 0)

        depreciated_months = min(
            elapsed_months,
            total_months,
        )

        accumulated_depreciation = money(
            monthly_depreciation
            * Decimal(depreciated_months)
        )

        accumulated_depreciation = min(
            accumulated_depreciation,
            depreciable_amount,
        )

        current_book_value = money(
            purchase_cost - accumulated_depreciation
        )

        current_book_value = max(
            current_book_value,
            residual_value,
        )

        remaining_months = max(
            total_months - depreciated_months,
            0,
        )

        if depreciable_amount > 0:
            depreciation_percent = money(
                accumulated_depreciation
                / depreciable_amount
                * Decimal("100")
            )
        else:
            depreciation_percent = Decimal("100.00")

        result = {
            "applicable": True,
            "as_of_date": calculation_date,
            "purchase_cost": purchase_cost,
            "residual_value": residual_value,
            "depreciable_amount": depreciable_amount,
            "useful_life_years": self.useful_life_years,
            "total_months": total_months,
            "elapsed_months": depreciated_months,
            "remaining_months": remaining_months,
            "annual_depreciation": annual_depreciation,
            "monthly_depreciation": monthly_depreciation,
            "accumulated_depreciation": accumulated_depreciation,
            "current_book_value": current_book_value,
            "depreciation_percent": depreciation_percent,
            "fully_depreciated": (
                depreciated_months >= total_months
            ),
            "tax_reference_rate": Decimal("15.00"),
            "tax_reference_method": "Written Down Value",
        }

        if self.status == "sold" and self.disposal_amount is not None:

            disposal_amount = money(
                self.disposal_amount
            )

            result["disposal_amount"] = disposal_amount
            result["disposal_gain_loss"] = money(
                disposal_amount - current_book_value
            )

        return result

    @property
    def current_book_value(self):
        snapshot = self.depreciation_snapshot()

        if not snapshot["applicable"]:
            return None

        return snapshot["current_book_value"]

    def __str__(self):
        return (
            f"{self.vehicle_code} - "
            f"{self.registration_number}"
        )