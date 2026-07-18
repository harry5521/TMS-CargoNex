from django.contrib import admin
from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):

    list_display = (
        "driver_code",
        "full_name",
        "cnic",
        "phone",
        "license_type",
        "license_expiry_date",
        "status",
        "driver_type",
    )

    list_filter = (
        "status",
        "driver_type",
        "license_type",
    )

    search_fields = (
        "driver_code",
        "full_name",
        "cnic",
        "phone",
        "license_number",
    )

    readonly_fields = (
        "driver_code",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )