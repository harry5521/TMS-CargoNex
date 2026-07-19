from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.services import record_transaction
from builty.models import Builty
from customers.models import Customer

from .models import Payment


VALID_PAYMENT_MODES = {
    value for value, _ in Payment.PAYMENT_MODES
}


def _money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Please enter a valid payment amount.")

    if amount <= 0:
        raise ValidationError(
            "Payment amount must be greater than zero."
        )

    return amount.quantize(Decimal("0.01"))


@transaction.atomic
def record_builty_payment(
    *,
    builty,
    amount,
    payment_mode="cash",
    payment_date=None,
    reference_no=None,
    remarks=None,
):
    """
    Records one Builty payment atomically:
      1. locks Builty and Customer,
      2. creates Payment,
      3. reduces Customer.current_balance,
      4. updates Builty advance/remaining/status,
      5. creates the cash ledger Transaction.

    Any failure rolls back every step.
    """

    builty_id = builty.pk if isinstance(builty, Builty) else builty

    try:
        locked_builty = (
            Builty.objects
            .select_for_update()
            .get(pk=builty_id)
        )

    except Builty.DoesNotExist:
        raise ValidationError(
            "Selected Builty does not exist."
        )

    customer = (
        Customer.objects
        .select_for_update()
        .get(pk=locked_builty.customer_id)
    )

    clean_amount = _money(amount)

    if locked_builty.document_status == "cancelled":
        raise ValidationError(
            "Payment cannot be recorded against a cancelled Builty."
        )

    if locked_builty.document_status != "finalized":
        raise ValidationError(
            "Payment can only be recorded against a finalized Builty."
        )

    if payment_mode not in VALID_PAYMENT_MODES:
        raise ValidationError("Please select a valid payment mode.")

    clean_reference = str(reference_no or "").strip()
    if payment_mode != "cash" and not clean_reference:
        raise ValidationError(
            "Reference number is required for non-cash payments."
        )

    outstanding = Decimal(locked_builty.remaining_amount or 0)

    if locked_builty.payment_status == "paid" or outstanding <= 0:
        raise ValidationError(
            "This Builty has already been fully paid."
        )

    if clean_amount > outstanding:
        raise ValidationError(
            "Payment amount cannot exceed the Builty outstanding amount."
        )

    current_balance = Decimal(customer.current_balance or 0)

    payment = Payment.objects.create(
        builty=locked_builty,
        amount=clean_amount,
        payment_mode=payment_mode,
        payment_date=payment_date or timezone.localdate(),
        reference_no=clean_reference or None,
        remarks=str(remarks).strip() if remarks else None,
    )

    customer.current_balance = current_balance - clean_amount
    customer.save(update_fields=["current_balance"])

    locked_builty.advance_amount = (
        Decimal(locked_builty.advance_amount or 0) + clean_amount
    )

    locked_builty._allow_financial_update = True
    locked_builty.save(
        update_fields=[
            "advance_amount",
            "remaining_amount",
            "payment_status",
            "updated_at",
        ]
    )

    ledger_remarks = str(remarks or "").strip()
    if payment.payment_id:
        payment_reference = f"Payment ID: {payment.payment_id}"
        ledger_remarks = (
            f"{ledger_remarks} | {payment_reference}"
            if ledger_remarks
            else payment_reference
        )

    cash_transaction = record_transaction(
        title=f"Payment against {locked_builty.builty_no}",
        amount=clean_amount,
        category_name="Customer Payment",
        category_type="income",
        customer=customer,
        builty=locked_builty,
        remarks=ledger_remarks,
        transaction_date=payment.payment_date,
    )

    return payment, cash_transaction
