from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from customers.models import Customer
from drivers.models import Driver
from payments.services import record_builty_payment
from vehicles.models import Vehicle

from .models import Builty


@transaction.atomic
def finalize_builty(*, builty_id):
    """
    Finalizes a Draft Builty in one atomic database transaction.

    Accounting flow:
      1. lock Builty, Customer, Vehicle and Driver,
      2. post full freight to Customer.current_balance,
      3. finalize the Builty,
      4. if an advance was entered on the Draft, create Payment,
         reduce Customer balance and create cash-in Transaction.

    Net customer balance increase is freight - advance.
    """

    try:
        # Sirf Builty row lock hogi.
        # Nullable Vehicle/Driver ko join nahi karna.
        builty = (
            Builty.objects
            .select_for_update()
            .get(pk=builty_id)
        )

    except Builty.DoesNotExist:
        raise ValidationError(
            "Builty not found."
        )

    if builty.document_status != "draft":
        raise ValidationError(
            "Only a Draft Builty can be finalized."
        )

    customer = (
        Customer.objects
        .select_for_update()
        .get(pk=builty.customer_id)
    )

    if not builty.vehicle_id:
        raise ValidationError(
            "Vehicle is required to finalize Builty."
        )

    if not builty.driver_id:
        raise ValidationError(
            "Driver is required to finalize Builty."
        )

    locked_vehicle = (
        Vehicle.objects
        .select_for_update()
        .get(pk=builty.vehicle_id)
    )

    locked_driver = (
        Driver.objects
        .select_for_update()
        .get(pk=builty.driver_id)
    )

    # Assign locked objects so model validation uses current database state.
    builty.vehicle = locked_vehicle
    builty.driver = locked_driver

    planned_advance = Decimal(builty.advance_amount or 0)
    freight = Decimal(builty.freight_amount or 0)

    # Advance entered on a Draft is only a planned/received-at-finalization
    # amount. Reset first, then post it through the centralized payment
    # service so Payment, customer balance, Builty and cash ledger stay synced.
    builty.advance_amount = Decimal("0.00")
    builty.document_status = "finalized"
    builty.finalized_at = timezone.now()
    builty.cancelled_at = None
    builty.cancel_reason = ""

    builty.full_clean()
    builty.save()

    customer.current_balance = (
        Decimal(customer.current_balance or 0) + freight
    )
    customer.save(update_fields=["current_balance"])

    payment = None
    cash_transaction = None

    if planned_advance > 0:
        payment, cash_transaction = record_builty_payment(
            builty=builty,
            amount=planned_advance,
            payment_mode="cash",
            payment_date=builty.builty_date,
            remarks=(
                f"Advance received while finalizing {builty.builty_no}."
            ),
        )

        # Refresh values updated by payment service.
        builty.refresh_from_db()

    from trips.services import ensure_trip_for_builty
    ensure_trip_for_builty(builty_id=builty.pk,)

    return builty, payment, cash_transaction


@transaction.atomic
def cancel_builty(*, builty_id, reason):
    clean_reason = str(reason or "").strip()

    if not clean_reason:
        raise ValidationError("Cancellation reason is required.")

    try:
        builty = (
            Builty.objects
            .select_for_update()
            .get(pk=builty_id)
        )

    except Builty.DoesNotExist:
        raise ValidationError(
            "Builty not found."
        )

    if builty.document_status == "cancelled":
        raise ValidationError("Builty is already cancelled.")

    if builty.dispatch_status != "pending":
        raise ValidationError(
            "A dispatched Builty cannot be cancelled from this screen."
        )

    # A payment must be explicitly reversed/refunded before cancellation.
    if builty.payments.exists():
        raise ValidationError(
            "This Builty has payment records. Reverse or refund them before cancellation."
        )

    if builty.document_status == "finalized":
        customer = (
            Customer.objects
            .select_for_update()
            .get(pk=builty.customer_id)
        )

        customer.current_balance = (
            Decimal(customer.current_balance or 0)
            - Decimal(builty.remaining_amount or 0)
        )
        customer.save(update_fields=["current_balance"])

    builty.document_status = "cancelled"
    builty.cancel_reason = clean_reason
    builty.cancelled_at = timezone.now()
    builty.save(
        update_fields=[
            "document_status",
            "cancel_reason",
            "cancelled_at",
            "updated_at",
        ]
    )

    from trips.services import cancel_pending_trip_for_builty

    cancel_pending_trip_for_builty(builty_id=builty.pk, reason=clean_reason,)

    return builty
