from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = (
        "vehicle_code",
        "registration_number",
        "vehicle_type",
        "body_type",
        "ownership_type",
        "capacity_tons",
        "status",
        "current_book_value_display",
    )

    list_filter = (
        "vehicle_type",
        "body_type",
        "ownership_type",
        "status",
    )

    search_fields = (
        "vehicle_code",
        "registration_number",
        "make",
        "model",
        "chassis_number",
        "engine_number",
        "owner_name",
    )

    readonly_fields = (
        "vehicle_code",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(
        description="Current Book Value"
    )
    def current_book_value_display(self, obj):

        value = obj.current_book_value

        if value is None:
            return "Not Applicable"

        return f"PKR {value:,.2f}"