from django.contrib import admin

from .models import Trip, TripExpense


class TripExpenseInline(admin.TabularInline):
    model = TripExpense
    extra = 0
    can_delete = False
    readonly_fields = (
        "expense_no",
        "title",
        "amount",
        "payment_mode",
        "reference_no",
        "expense_date",
        "remarks",
        "created_at",
        "updated_at",
    )


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "trip_no",
        "builty",
        "driver",
        "vehicle",
        "scheduled_date",
        "status",
        "started_at",
        "completed_at",
    )
    list_filter = ("status", "scheduled_date")
    search_fields = (
        "trip_no",
        "builty__builty_no",
        "builty__customer__company_name",
        "driver__full_name",
        "vehicle__registration_number",
    )
    readonly_fields = (
        "trip_no",
        "builty",
        "driver",
        "vehicle",
        "scheduled_date",
        "status",
        "started_at",
        "completed_at",
        "cancelled_at",
        "cancel_reason",
        "created_at",
        "updated_at",
    )
    inlines = [TripExpenseInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TripExpense)
class TripExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "expense_no",
        "trip",
        "title",
        "amount",
        "payment_mode",
        "expense_date",
    )
    list_filter = ("payment_mode", "expense_date")
    search_fields = (
        "expense_no",
        "trip__trip_no",
        "trip__builty__builty_no",
        "title",
    )
    readonly_fields = (
        "expense_no",
        "trip",
        "title",
        "amount",
        "payment_mode",
        "reference_no",
        "expense_date",
        "remarks",
        "created_at",
        "updated_at",
    )

    def has_delete_permission(self, request, obj=None):
        return False
