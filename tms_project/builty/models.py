from django.db import models
from customers.models import Customer


class Builty(models.Model):

    PAYMENT_STATUS = (
        ('paid', 'Paid'),
        ('topay', 'To Pay'),
        ('partial', 'Partial'),
    )

    # =========================
    # BASIC INFO
    # =========================

    builty_no = models.CharField(
        max_length=20,
        unique=True
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='builties'
    )

    # =========================
    # CONSIGNEE (RECEIVER)
    # =========================

    receiver_name = models.CharField(
        max_length=150
    )

    receiver_phone = models.CharField(
        max_length=20
    )

    # =========================
    # SHIPMENT DETAILS
    # =========================

    origin_city = models.CharField(
        max_length=100
    )

    destination_city = models.CharField(
        max_length=100
    )

    goods_description = models.TextField()

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    package_count = models.PositiveIntegerField()

    # =========================
    # FREIGHT DETAILS
    # =========================

    total_freight = models.DecimalField(
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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.builty_no} - {self.customer.name}"