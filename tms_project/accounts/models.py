from django.db import models
from customers.models import Customer
from builty.models import Builty


class TransactionCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Transaction Categories'

    def __str__(self):
        return self.name


class Transaction(models.Model):

    TRANSACTION_TYPES = (
        ('cash_in', 'Cash In'),
        ('cash_out', 'Cash Out'),
    )

    transaction_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.PROTECT,
        related_name='transactions'
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )

    builty = models.ForeignKey(
        Builty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    transaction_date = models.DateField(
        auto_now_add=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.transaction_id:

            last_transaction = (
                Transaction.objects
                .order_by('-id')
                .first()
            )

            if last_transaction:

                last_number = int(
                    last_transaction.transaction_id.split('-')[1]
                )

                next_number = last_number + 1

            else:

                next_number = 1001

            self.transaction_id = (
                f"TXN-{next_number}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.transaction_id} "
            f"- {self.amount}"
        )