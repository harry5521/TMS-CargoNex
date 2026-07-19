from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from accounts.models import Transaction
from accounts.services import record_transaction
from builty.models import Builty
from drivers.models import Driver
from vehicles.models import Vehicle

from .models import ACTIVE_TRIP_STATUSES, Trip, TripExpense


def _first_validation_message(exc):
    if hasattr(exc, "message_dict"):
        for errors in exc.message_dict.values():
            if errors:
                return str(errors[0])
    return exc.messages[0] if exc.messages else str(exc)


@transaction.atomic
def ensure_trip_for_builty(*, builty_id):
    """
    Create the one-to-one pending Trip for a finalized Builty.

    This is used automatically after Builty finalization and manually by the
    Assign Trip fallback screen for legacy/finalized Builties without a Trip.
    """

    try:
        builty = (
            Builty.objects
            .select_for_update()
            .get(pk=builty_id)
        )
    except Builty.DoesNotExist:
        raise ValidationError("Builty not found.")

    if builty.document_status != "finalized":
        raise ValidationError("Only a finalized Builty can be assigned.")

    if builty.dispatch_status != "pending":
        raise ValidationError(
            "Only a pending-dispatch Builty can be assigned to a new Trip."
        )

    if not builty.vehicle_id:
        raise ValidationError("Builty does not have an assigned vehicle.")

    if not builty.driver_id:
        raise ValidationError("Builty does not have an assigned driver.")

    vehicle = (
        Vehicle.objects
        .select_for_update()
        .get(pk=builty.vehicle_id)
    )

    driver = (
        Driver.objects
        .select_for_update()
        .get(pk=builty.driver_id)
    )

    try:
        trip = (
            Trip.objects
            .select_for_update()
            .get(builty_id=builty.pk)
        )
        created = False
    except Trip.DoesNotExist:
        try:
            trip = Trip.objects.create(
                builty=builty,
                driver=driver,
                vehicle=vehicle,
                scheduled_date=builty.builty_date,
                status="pending",
            )
            created = True
        except IntegrityError:
            trip = (
                Trip.objects
                .select_for_update()
                .get(builty_id=builty.pk)
            )
            created = False

    if not created:
        if trip.status != "pending":
            return trip

        trip.driver = driver
        trip.vehicle = vehicle
        trip.scheduled_date = builty.builty_date

    trip.full_clean()
    trip.save()
    return trip


@transaction.atomic
def sync_pending_trip_from_builty(*, builty_id):
    try:
        builty = (
            Builty.objects
            .select_for_update()
            .get(pk=builty_id)
        )
    except Builty.DoesNotExist:
        raise ValidationError("Builty not found.")

    try:
        trip = (
            Trip.objects
            .select_for_update()
            .get(builty_id=builty.pk)
        )
    except Trip.DoesNotExist:
        if builty.document_status == "finalized":
            return ensure_trip_for_builty(builty_id=builty.pk)
        return None

    if trip.status != "pending":
        return trip

    if not builty.vehicle_id or not builty.driver_id:
        raise ValidationError(
            "A finalized pending Builty must keep a driver and vehicle assigned."
        )

    vehicle = (
        Vehicle.objects
        .select_for_update()
        .get(pk=builty.vehicle_id)
    )

    driver = (
        Driver.objects
        .select_for_update()
        .get(pk=builty.driver_id)
    )

    trip.vehicle = vehicle
    trip.driver = driver
    trip.scheduled_date = builty.builty_date
    trip.full_clean()
    trip.save(
        update_fields=[
            "vehicle",
            "driver",
            "scheduled_date",
            "updated_at",
        ]
    )
    return trip


@transaction.atomic
def start_trip(*, trip_id):
    try:
        trip_reference = Trip.objects.only("id", "builty_id").get(pk=trip_id)
    except Trip.DoesNotExist:
        raise ValidationError("Trip not found.")

    builty = (
        Builty.objects
        .select_for_update()
        .get(pk=trip_reference.builty_id)
    )

    if not builty.vehicle_id or not builty.driver_id:
        raise ValidationError("Builty must have a driver and vehicle assigned.")

    vehicle = (
        Vehicle.objects
        .select_for_update()
        .get(pk=builty.vehicle_id)
    )

    driver = (
        Driver.objects
        .select_for_update()
        .get(pk=builty.driver_id)
    )

    trip = (
        Trip.objects
        .select_for_update()
        .get(pk=trip_id)
    )

    if trip.status != "pending":
        raise ValidationError("Only a pending Trip can be started.")

    if builty.document_status != "finalized":
        raise ValidationError("Trip Builty is not finalized.")

    if builty.dispatch_status != "pending":
        raise ValidationError("Builty is not pending dispatch.")

    if vehicle.status != "available":
        raise ValidationError("Assigned vehicle is not available.")

    if driver.status != "active":
        raise ValidationError("Assigned driver is not active.")

    if driver.license_expiry_date < timezone.localdate():
        raise ValidationError("Assigned driver's licence has expired.")

    if (
        Trip.objects
        .exclude(pk=trip.pk)
        .filter(
            driver_id=driver.pk,
            status="in_transit",
        )
        .exists()
    ):
        raise ValidationError("Driver is already on another active Trip.")

    if (
        Trip.objects
        .exclude(pk=trip.pk)
        .filter(
            vehicle_id=vehicle.pk,
            status="in_transit",
        )
        .exists()
    ):
        raise ValidationError("Vehicle is already on another active Trip.")

    now = timezone.now()

    trip.driver = driver
    trip.vehicle = vehicle
    trip.status = "in_transit"
    trip.started_at = now
    trip.completed_at = None
    trip.full_clean()
    trip.save(
        update_fields=[
            "driver",
            "vehicle",
            "status",
            "started_at",
            "completed_at",
            "updated_at",
        ]
    )

    builty.dispatch_status = "transit"
    builty.save(update_fields=["dispatch_status", "updated_at"])

    vehicle.status = "on_trip"
    vehicle.save(update_fields=["status", "updated_at"])

    return trip


@transaction.atomic
def complete_trip(*, trip_id):
    try:
        trip_reference = Trip.objects.only("id", "builty_id", "vehicle_id").get(
            pk=trip_id
        )
    except Trip.DoesNotExist:
        raise ValidationError("Trip not found.")

    builty = (
        Builty.objects
        .select_for_update()
        .get(pk=trip_reference.builty_id)
    )

    vehicle = (
        Vehicle.objects
        .select_for_update()
        .get(pk=trip_reference.vehicle_id)
    )

    trip = (
        Trip.objects
        .select_for_update()
        .get(pk=trip_id)
    )

    if trip.status != "in_transit":
        raise ValidationError("Only an in-transit Trip can be completed.")

    trip.status = "completed"
    trip.completed_at = timezone.now()
    trip.full_clean()
    trip.save(
        update_fields=[
            "status",
            "completed_at",
            "updated_at",
        ]
    )

    builty.dispatch_status = "completed"
    builty.save(update_fields=["dispatch_status", "updated_at"])

    vehicle.status = "available"
    vehicle.save(update_fields=["status", "updated_at"])

    return trip


@transaction.atomic
def cancel_pending_trip_for_builty(*, builty_id, reason):
    try:
        trip = (
            Trip.objects
            .select_for_update()
            .get(builty_id=builty_id)
        )
    except Trip.DoesNotExist:
        return None

    if trip.status == "cancelled":
        return trip

    if trip.status != "pending":
        raise ValidationError(
            "Only a pending Trip can be cancelled with its Builty."
        )

    trip.status = "cancelled"
    trip.cancel_reason = str(reason or "").strip() or "Builty cancelled."
    trip.cancelled_at = timezone.now()
    trip.full_clean()
    trip.save(
        update_fields=[
            "status",
            "cancel_reason",
            "cancelled_at",
            "updated_at",
        ]
    )
    return trip


@transaction.atomic
def create_trip_expense(*, trip_id, cleaned_data):
    try:
        trip = (
            Trip.objects
            .select_for_update()
            .get(pk=trip_id)
        )
    except Trip.DoesNotExist:
        raise ValidationError("Trip not found.")

    if trip.status == "cancelled":
        raise ValidationError("Expense cannot be added to a cancelled Trip.")

    expense = TripExpense(
        trip=trip,
        **cleaned_data,
    )
    expense.full_clean()
    expense.save()

    ledger = record_transaction(
        title=f"{expense.title} - {trip.trip_no}",
        amount=expense.amount,
        category_name="Trip Expense",
        category_type="expense",
        transaction_type="cash_out",
        builty=trip.builty,
        trip=trip,
        trip_expense=expense,
        remarks=(
            f"Trip expense {expense.expense_no}. "
            f"Mode: {expense.get_payment_mode_display()}."
            + (f" Reference: {expense.reference_no}." if expense.reference_no else "")
            + (f" {expense.remarks}" if expense.remarks else "")
        ),
        transaction_date=expense.expense_date,
    )

    return expense, ledger


@transaction.atomic
def update_trip_expense_title(*, expense_id, title):
    try:
        expense = (
            TripExpense.objects
            .select_for_update()
            .select_related("trip")
            .get(pk=expense_id)
        )
    except TripExpense.DoesNotExist:
        raise ValidationError("Trip expense not found.")

    clean_title = str(title or "").strip()
    if not clean_title:
        raise ValidationError("Expense title is required.")

    expense.title = clean_title
    expense.save(update_fields=["title", "updated_at"])

    try:
        ledger = (
            Transaction.objects
            .select_for_update()
            .get(trip_expense_id=expense.pk)
        )
    except Transaction.DoesNotExist:
        raise ValidationError(
            "Linked ledger transaction is missing for this expense."
        )

    ledger.title = f"{clean_title} - {expense.trip.trip_no}"
    ledger.save(update_fields=["title", "updated_at"])

    return expense
