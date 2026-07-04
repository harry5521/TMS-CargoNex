
from django.db import models
from django.utils import timezone
from builty.models import Builty


class Payment(models.Model):

    PAYMENT_MODES = (
        ("cash", "Cash"),
        ("bank", "Bank Transfer"),
        ("online", "Online Transfer"),
        ("cheque", "Cheque"),
    )

    payment_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    builty = models.ForeignKey(
        Builty,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODES,
        default="cash"
    )

    reference_no = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    payment_date = models.DateField(
        default=timezone.now
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.payment_id:

            last_payment = (
                Payment.objects
                .order_by("-id")
                .first()
            )

            if last_payment:

                last_number = int(
                    last_payment.payment_id.split("-")[1]
                )

                next_number = last_number + 1

            else:

                next_number = 1001

            self.payment_id = (
                f"PAY-{next_number}"
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.payment_id