from django import forms

from .models import Vehicle


class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicle

        fields = [
            "registration_number",
            "vehicle_type",
            "body_type",
            "make",
            "model",
            "model_year",
            "color",
            "chassis_number",
            "engine_number",
            "capacity_tons",

            "ownership_type",
            "owner_name",
            "owner_phone",

            "purchase_date",
            "purchase_cost",
            "depreciation_start_date",
            "residual_value",
            "useful_life_years",

            "status",
            "disposal_date",
            "disposal_amount",
            "notes",
        ]

    def clean_registration_number(self):
        value = self.cleaned_data.get(
            "registration_number",
            ""
        ).strip().upper()

        queryset = Vehicle.objects.filter(
            registration_number__iexact=value
        )

        if self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise forms.ValidationError(
                "A vehicle with this registration number already exists."
            )

        return value

    def clean_chassis_number(self):
        value = self.cleaned_data.get(
            "chassis_number"
        )

        if not value:
            return None

        value = value.strip().upper()

        queryset = Vehicle.objects.filter(
            chassis_number__iexact=value
        )

        if self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise forms.ValidationError(
                "A vehicle with this chassis number already exists."
            )

        return value

    def clean_engine_number(self):
        value = self.cleaned_data.get(
            "engine_number"
        )

        if not value:
            return None

        value = value.strip().upper()

        queryset = Vehicle.objects.filter(
            engine_number__iexact=value
        )

        if self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise forms.ValidationError(
                "A vehicle with this engine number already exists."
            )

        return value

    def clean_make(self):
        value = self.cleaned_data.get("make")
        return value.strip() if value else None

    def clean_model(self):
        value = self.cleaned_data.get("model")
        return value.strip() if value else None

    def clean_color(self):
        value = self.cleaned_data.get("color")
        return value.strip() if value else None

    def clean_owner_name(self):
        value = self.cleaned_data.get("owner_name")
        return value.strip() if value else None

    def clean_owner_phone(self):
        value = self.cleaned_data.get("owner_phone")
        return value.strip() if value else None

    def clean_notes(self):
        value = self.cleaned_data.get("notes")
        return value.strip() if value else None

    def clean(self):
        cleaned_data = super().clean()

        ownership_type = cleaned_data.get(
            "ownership_type"
        )

        status = cleaned_data.get("status")

        purchase_date = cleaned_data.get(
            "purchase_date"
        )

        purchase_cost = cleaned_data.get(
            "purchase_cost"
        )

        depreciation_start_date = cleaned_data.get(
            "depreciation_start_date"
        )

        residual_value = cleaned_data.get(
            "residual_value"
        )

        owner_name = cleaned_data.get(
            "owner_name"
        )

        disposal_date = cleaned_data.get(
            "disposal_date"
        )

        disposal_amount = cleaned_data.get(
            "disposal_amount"
        )

        if ownership_type == "company_owned":

            if not purchase_date:
                self.add_error(
                    "purchase_date",
                    "Purchase date is required."
                )

            if not purchase_cost:
                self.add_error(
                    "purchase_cost",
                    "Purchase cost is required."
                )

            if not depreciation_start_date:
                self.add_error(
                    "depreciation_start_date",
                    "Depreciation start date is required."
                )

            if (
                purchase_date
                and depreciation_start_date
                and depreciation_start_date < purchase_date
            ):
                self.add_error(
                    "depreciation_start_date",
                    "Depreciation start date cannot be before purchase date."
                )

            if (
                purchase_cost is not None
                and residual_value is not None
                and residual_value >= purchase_cost
            ):
                self.add_error(
                    "residual_value",
                    "Expected resale value must be less than purchase cost."
                )

            cleaned_data["owner_name"] = None
            cleaned_data["owner_phone"] = None

        else:

            if not owner_name:
                self.add_error(
                    "owner_name",
                    "Owner name is required for attached or market vehicles."
                )

            cleaned_data["purchase_date"] = None
            cleaned_data["purchase_cost"] = None
            cleaned_data["depreciation_start_date"] = None
            cleaned_data["residual_value"] = 0

        if status == "sold":

            if not disposal_date:
                self.add_error(
                    "disposal_date",
                    "Sale date is required for a sold vehicle."
                )

            if disposal_amount is None:
                self.add_error(
                    "disposal_amount",
                    "Sale amount is required for a sold vehicle."
                )

        else:
            cleaned_data["disposal_date"] = None
            cleaned_data["disposal_amount"] = None

        return cleaned_data