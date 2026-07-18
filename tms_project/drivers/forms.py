from django import forms
from django.utils import timezone

from .models import Driver


class DriverForm(forms.ModelForm):

    class Meta:
        model = Driver

        fields = [
            "full_name",
            "father_name",
            "cnic",
            "date_of_birth",
            "driver_type",
            "phone",
            "alternate_phone",
            "city",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "license_number",
            "license_type",
            "license_issue_date",
            "license_expiry_date",
            "license_authority",
            "joining_date",
            "status",
            "notes",
        ]

        labels = {
            "full_name": "Full Name",
            "father_name": "Father Name",
            "cnic": "CNIC",
            "date_of_birth": "Date of Birth",
            "driver_type": "Driver Type",
            "phone": "Phone",
            "alternate_phone": "Alternate Phone",
            "city": "City",
            "address": "Address",
            "emergency_contact_name": "Emergency Contact Name",
            "emergency_contact_phone": "Emergency Contact Phone",
            "license_number": "License Number",
            "license_type": "License Type",
            "license_issue_date": "License Issue Date",
            "license_expiry_date": "License Expiry Date",
            "license_authority": "License Authority",
            "joining_date": "Joining Date",
            "status": "Status",
            "notes": "Notes",
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name", "")
        return full_name.strip()

    def clean_father_name(self):
        value = self.cleaned_data.get("father_name")
        return value.strip() if value else None

    def clean_cnic(self):
        cnic = self.cleaned_data.get("cnic", "").strip()

        digits_only = cnic.replace("-", "")

        if not digits_only.isdigit():
            raise forms.ValidationError(
                "CNIC must contain only digits or dashes."
            )

        if len(digits_only) != 13:
            raise forms.ValidationError(
                "CNIC must be exactly 13 digits."
            )

        # Save CNIC in standard format: 35202-1234567-1
        formatted_cnic = (
            f"{digits_only[:5]}-"
            f"{digits_only[5:12]}-"
            f"{digits_only[12]}"
        )

        qs = Driver.objects.filter(cnic=formatted_cnic)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "Driver with this CNIC already exists."
            )

        return formatted_cnic

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not phone:
            raise forms.ValidationError(
                "Phone number is required."
            )

        return phone

    def clean_alternate_phone(self):
        value = self.cleaned_data.get("alternate_phone")
        return value.strip() if value else None

    def clean_city(self):
        value = self.cleaned_data.get("city")
        return value.strip() if value else None

    def clean_address(self):
        value = self.cleaned_data.get("address")
        return value.strip() if value else None

    def clean_emergency_contact_name(self):
        value = self.cleaned_data.get("emergency_contact_name")
        return value.strip() if value else None

    def clean_emergency_contact_phone(self):
        value = self.cleaned_data.get("emergency_contact_phone")
        return value.strip() if value else None

    def clean_license_number(self):
        license_number = self.cleaned_data.get(
            "license_number",
            ""
        ).strip()

        if not license_number:
            raise forms.ValidationError(
                "License number is required."
            )

        qs = Driver.objects.filter(
            license_number__iexact=license_number
        )

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "Driver with this license number already exists."
            )

        return license_number.upper()

    def clean_license_authority(self):
        value = self.cleaned_data.get("license_authority")
        return value.strip() if value else None

    def clean_notes(self):
        value = self.cleaned_data.get("notes")
        return value.strip() if value else None

    def clean(self):
        cleaned_data = super().clean()

        issue_date = cleaned_data.get("license_issue_date")
        expiry_date = cleaned_data.get("license_expiry_date")

        if issue_date and expiry_date:
            if expiry_date < issue_date:
                self.add_error(
                    "license_expiry_date",
                    "License expiry date cannot be before issue date."
                )

        # Warning nahi, hard block rakh raha hon.
        # Agar expired license driver allow karna ho to ye block remove kar dena.
        if expiry_date and expiry_date < timezone.localdate():
            self.add_error(
                "license_expiry_date",
                "License expiry date cannot be in the past."
            )

        return cleaned_data