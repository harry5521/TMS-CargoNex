from django.db import models
from customers.models import Customer
from builty.models import Builty
from django.utils import timezone


from django.db import models


class TransactionCategory(models.Model):

    CATEGORY_TYPES = (
        ("expense", "Expense"),
        ("income", "Income"),
        ("owner", "Owner Transaction"),
    )

    CASH_FLOWS = (
        ("cash_in", "Cash In"),
        ("cash_out", "Cash Out"),
    )

    OWNER_ACTIONS = (
        ("investment", "Investment"),
        ("withdrawal", "Withdrawal"),
    )

    name = models.CharField(
        max_length=100,
        unique=True
    )

    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPES
    )

    cash_flow = models.CharField(
        max_length=10,
        choices=CASH_FLOWS,
        editable=False
    )

    owner_action = models.CharField(
        max_length=20,
        choices=OWNER_ACTIONS,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Transaction Categories"

    def save(self, *args, **kwargs):

        if self.category_type == "expense":

            self.cash_flow = "cash_out"
            self.owner_action = None

        elif self.category_type == "income":

            self.cash_flow = "cash_in"
            self.owner_action = None

        elif self.category_type == "owner":

            if self.owner_action == "investment":

                self.cash_flow = "cash_in"

            elif self.owner_action == "withdrawal":

                self.cash_flow = "cash_out"

            else:

                raise ValueError(
                    "Owner action is required for Owner Transaction."
                )

        super().save(*args, **kwargs)

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

    title = models.CharField(
        max_length=200
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )

    builty = models.ForeignKey(
        Builty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
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
        default=timezone.now
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        if not self.transaction_type:
            self.transaction_type = self.category.cash_flow

        if not self.transaction_id:

            last = Transaction.objects.order_by("-id").first()

            next_number = (
                int(last.transaction_id.split("-")[1]) + 1
                if last else 1001
            )

            self.transaction_id = f"TXN-{next_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.title}"