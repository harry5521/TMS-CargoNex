from decimal import Decimal

from django import forms

from .models import Builty


class BuiltyForm(forms.ModelForm):

    class Meta:
        model = Builty
        fields = [
            "customer",
            "builty_date",
            "receiver_name",
            "receiver_phone",
            "origin_city",
            "destination_city",
            "goods_description",
            "weight",
            "package_count",
            "freight_amount",
            "advance_amount",
            "vehicle",
            "driver",
            "notes",
        ]

    def __init__(
        self,
        *args,
        lock_financial_fields=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.lock_financial_fields = lock_financial_fields

        for field_name, field in self.fields.items():
            field.required = field_name in {"customer", "builty_date"}

        self._original_financial_values = {
            "customer_id": self.instance.customer_id,
            "builty_date": self.instance.builty_date,
            "freight_amount": Decimal(
                self.instance.freight_amount or 0
            ),
            "advance_amount": Decimal(
                self.instance.advance_amount or 0
            ),
        }

    @staticmethod
    def _strip(value):
        return value.strip() if value else ""

    def clean_receiver_name(self):
        return self._strip(self.cleaned_data.get("receiver_name"))

    def clean_receiver_phone(self):
        value = self._strip(self.cleaned_data.get("receiver_phone"))
        return value or None

    def clean_origin_city(self):
        return self._strip(self.cleaned_data.get("origin_city"))

    def clean_destination_city(self):
        return self._strip(self.cleaned_data.get("destination_city"))

    def clean_goods_description(self):
        return self._strip(self.cleaned_data.get("goods_description"))

    def clean_notes(self):
        value = self._strip(self.cleaned_data.get("notes"))
        return value or None

    def clean(self):
        cleaned_data = super().clean()

        for field_name in (
            "weight",
            "freight_amount",
            "advance_amount",
        ):
            if cleaned_data.get(field_name) is None:
                cleaned_data[field_name] = Decimal("0.00")

        freight = Decimal(cleaned_data.get("freight_amount") or 0)
        advance = Decimal(cleaned_data.get("advance_amount") or 0)

        if advance > freight:
            self.add_error(
                "advance_amount",
                "Advance amount cannot be greater than freight amount.",
            )

        if self.lock_financial_fields and self.instance.pk:
            customer = cleaned_data.get("customer")
            builty_date = cleaned_data.get("builty_date")

            changed = []

            if (
                customer
                and customer.pk
                != self._original_financial_values["customer_id"]
            ):
                changed.append("Customer")

            if (
                builty_date
                != self._original_financial_values["builty_date"]
            ):
                changed.append("Builty Date")

            if (
                freight
                != self._original_financial_values["freight_amount"]
            ):
                changed.append("Freight Amount")

            if (
                advance
                != self._original_financial_values["advance_amount"]
            ):
                changed.append("Advance Amount")

            if changed:
                raise forms.ValidationError(
                    "Finalized Builty financial fields cannot be edited: "
                    + ", ".join(changed)
                    + "."
                )

        return cleaned_data
