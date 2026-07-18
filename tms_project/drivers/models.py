from django.db import models
from django.utils import timezone


class Driver(models.Model):

    DRIVER_TYPES = (
        ("company", "Company Driver"),
        ("contract", "Contract Driver"),
        ("external", "External / Market Driver"),
    )

    LICENSE_TYPES = (
        ("htv", "HTV"),
        ("ltv", "LTV"),
        ("psv", "PSV"),
        ("other", "Other"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("on_leave", "On Leave"),
        ("suspended", "Suspended"),
        ("inactive", "Inactive"),
    )

    # -------------------------
    # System Info
    # -------------------------

    driver_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        editable=False,
    )

    # -------------------------
    # Personal Info
    # -------------------------

    full_name = models.CharField(
        max_length=150
    )

    father_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    cnic = models.CharField(
        max_length=15,
        unique=True,
        help_text="Format: 35202-1234567-1"
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    driver_type = models.CharField(
        max_length=20,
        choices=DRIVER_TYPES,
        default="company"
    )

    # -------------------------
    # Contact Info
    # -------------------------

    phone = models.CharField(
        max_length=20
    )

    alternate_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    emergency_contact_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # -------------------------
    # License Info
    # -------------------------

    license_number = models.CharField(
        max_length=50,
        unique=True
    )

    license_type = models.CharField(
        max_length=20,
        choices=LICENSE_TYPES,
        default="htv"
    )

    license_issue_date = models.DateField(
        blank=True,
        null=True
    )

    license_expiry_date = models.DateField()

    license_authority = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # -------------------------
    # Employment / Status
    # -------------------------

    joining_date = models.DateField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # -------------------------
    # Save
    # -------------------------

    def save(self, *args, **kwargs):

        creating = self._state.adding

        super().save(*args, **kwargs)

        if creating and not self.driver_code:

            driver_code = f"DRV-{self.pk:06d}"

            type(self).objects.filter(
                pk=self.pk
            ).update(
                driver_code=driver_code
            )

            self.driver_code = driver_code

    # -------------------------
    # Helper Properties
    # -------------------------

    @property
    def is_license_expired(self):

        return self.license_expiry_date < timezone.localdate()

    @property
    def license_expiry_status(self):

        today = timezone.localdate()

        if self.license_expiry_date < today:

            return "expired"

        days_left = (
            self.license_expiry_date - today
        ).days

        if days_left <= 30:

            return "expiring_soon"

        return "valid"

    @property
    def can_be_assigned_to_trip(self):

        return (
            self.status == "active"
            and not self.is_license_expired
        )

    def __str__(self):

        return f"{self.driver_code} - {self.full_name}"