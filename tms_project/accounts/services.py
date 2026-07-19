from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Transaction, TransactionCategory


VALID_CATEGORY_TYPES = {
    value for value, _ in TransactionCategory.CATEGORY_TYPES
}


def _money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Transaction amount is invalid.")

    if amount <= 0:
        raise ValidationError(
            "Transaction amount must be greater than zero."
        )

    return amount.quantize(Decimal("0.01"))


def get_or_create_transaction_category(
    *,
    name,
    category_type,
    owner_action=None,
):
    name = str(name or "").strip()

    if not name:
        raise ValidationError("Transaction category name is required.")

    if category_type not in VALID_CATEGORY_TYPES:
        raise ValidationError("Invalid transaction category type.")

    if category_type == "owner" and owner_action not in {
        "investment",
        "withdrawal",
    }:
        raise ValidationError(
            "Owner action is required for an owner transaction category."
        )

    defaults = {
        "category_type": category_type,
        "owner_action": owner_action if category_type == "owner" else None,
    }

    category = (
        TransactionCategory.objects
        .filter(name__iexact=name)
        .first()
    )

    if category is None:
        try:
            category, _ = TransactionCategory.objects.get_or_create(
                name=name,
                defaults=defaults,
            )
        except IntegrityError:
            category = (
                TransactionCategory.objects
                .filter(name__iexact=name)
                .get()
            )

    if category.category_type != category_type:
        raise ValidationError(
            f'Category "{name}" already exists with a different type.'
        )

    expected_owner_action = (
        owner_action if category_type == "owner" else None
    )
    if category.owner_action != expected_owner_action:
        raise ValidationError(
            f'Category "{name}" has incompatible owner settings.'
        )

    return category


@transaction.atomic
def record_transaction(
    *,
    title,
    amount,
    category=None,
    category_name=None,
    category_type=None,
    owner_action=None,
    transaction_type=None,
    customer=None,
    builty=None,
    trip=None,
    trip_expense=None,
    remarks=None,
    transaction_date=None,
):
    """
    Global cash-ledger helper.

    Use this function everywhere instead of directly calling
    Transaction.objects.create(...). It validates category direction and can
    safely create a missing category.

    Important: this model is a CASH ledger. A freight receivable is not cash
    income and must not be recorded here until money is actually received.
    """

    clean_title = str(title or "").strip()
    if not clean_title:
        raise ValidationError("Transaction title is required.")

    clean_amount = _money(amount)

    if category is None:
        if not category_name or not category_type:
            raise ValidationError(
                "Provide either a category object or category name and type."
            )

        category = get_or_create_transaction_category(
            name=category_name,
            category_type=category_type,
            owner_action=owner_action,
        )

    expected_type = category.cash_flow

    if transaction_type and transaction_type != expected_type:
        raise ValidationError(
            "Transaction type does not match the selected category cash flow."
        )

    return Transaction.objects.create(
        title=clean_title,
        transaction_type=expected_type,
        category=category,
        customer=customer,
        builty=builty,
        trip=trip,
        trip_expense=trip_expense,
        amount=clean_amount,
        remarks=str(remarks).strip() if remarks else None,
        transaction_date=transaction_date or timezone.localdate(),
    )
