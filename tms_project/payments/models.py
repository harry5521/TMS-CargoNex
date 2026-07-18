
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
        null=True,
        blank=True,
        editable=False
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
        creating = self._state.adding

        super().save(*args, **kwargs)

        if creating and not self.payment_id:
            payment_id = f"PAY-{self.pk:06d}"

            type(self).objects.filter(
                pk=self.pk
            ).update(
                payment_id=payment_id
            )

            self.payment_id = payment_id

    def __str__(self):
        return self.payment_id