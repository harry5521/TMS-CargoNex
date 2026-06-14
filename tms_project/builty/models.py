from django.db import models
from django.utils import timezone
from customers.models import Customer


class Builty(models.Model):

    PAYMENT_STATUS = (
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('topay', 'To Pay'),
    )

    DISPATCH_STATUS = (
        ('pending', 'Pending Dispatch'),
        ('transit', 'In Transit'),
        ('completed', 'Completed'),
    )

    # =========================
    # BASIC INFO
    # =========================

    builty_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='builties'
    )

    builty_date = models.DateField(default=timezone.now)

    # =========================
    # CONSIGNEE
    # =========================

    receiver_name = models.CharField(
        max_length=150
    )

    receiver_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # =========================
    # ROUTE
    # =========================

    origin_city = models.CharField(
        max_length=100
    )

    destination_city = models.CharField(
        max_length=100
    )

    # =========================
    # SHIPMENT
    # =========================

    goods_description = models.CharField(
        max_length=255
    )

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    package_count = models.PositiveIntegerField(null=True, blank=True)

    # =========================
    # FREIGHT
    # =========================

    freight_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    advance_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    remaining_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='topay'
    )

    # =========================
    # DISPATCH
    # =========================

    dispatch_status = models.CharField(
        max_length=15,
        choices=DISPATCH_STATUS,
        default='pending'
    )

    # =========================
    # VEHICLE & DRIVER
    # =========================

    vehicle_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    driver_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    driver_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # =========================
    # NOTES
    # =========================

    notes = models.TextField(
        blank=True,
        null=True
    )

    # =========================
    # TIMESTAMPS
    # =========================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def route(self):
        return f"{self.origin_city} → {self.destination_city}"

    def save(self, *args, **kwargs):

        if not self.builty_no:

            last_builty = (
                Builty.objects
                .order_by('-id')
                .first()
            )

            if last_builty:

                last_number = int(
                    last_builty.builty_no.split('-')[1]
                )

                next_number = last_number + 1

            else:

                next_number = 1001

            self.builty_no = f"BLT-{next_number}"

        self.remaining_amount = (
            self.freight_amount -
            self.advance_amount
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.builty_no