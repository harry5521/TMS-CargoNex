from django.contrib import admin

from .models import Builty


@admin.register(Builty)
class BuiltyAdmin(admin.ModelAdmin):
    list_display = (
        "builty_no",
        "customer",
        "route_display",
        "document_status",
        "payment_status",
        "dispatch_status",
        "vehicle_number",
        "driver_name",
        "builty_date",
    )

    list_filter = (
        "document_status",
        "payment_status",
        "dispatch_status",
        "builty_date",
    )

    search_fields = (
        "builty_no",
        "customer__company_name",
        "origin_city",
        "destination_city",
        "vehicle_number",
        "driver_name",
    )

    readonly_fields = (
        "builty_no",
        "remaining_amount",
        "payment_status",
        "finalized_at",
        "cancelled_at",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "customer",
        "vehicle",
        "driver",
    )

    @admin.display(description="Route")
    def route_display(self, obj):
        return obj.route
