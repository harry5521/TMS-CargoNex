from django.db import models
from django.db.models import Max

# Create your models here.

class Customer(models.Model):

    CUSTOMER_TYPES = (
        ('regular', 'Regular'),
        ('walkin', 'Walk-In'),
    )

    customer_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    company_name = models.CharField(
        max_length=200
    )

    cnic_ntn = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    contact_person = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='walkin'
    )

    current_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
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

    @property
    def balance_status(self):
        if self.current_balance > 0:
            return "Due"
        elif self.current_balance < 0:
            return "Advance"
        else:
            return "Clear"

    def save(self, *args, **kwargs):
        if not self.customer_id:
            # Get the highest customer_id string currently in the database
            max_id = Customer.objects.aggregate(Max('customer_id'))['customer_id__max']
            
            if max_id:
                # max_id looks like "CUS-1001". Split by "-" and take the number part.
                try:
                    last_number = int(max_id.split('-')[1])
                    next_id = last_number + 1
                except (IndexError, ValueError):
                    # Fallback if the string format was somehow mutated
                    next_id = 1001
            else:
                # If the database is completely empty
                next_id = 1001
                
            self.customer_id = f"CUS-{next_id}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_id} - {self.company_name}"