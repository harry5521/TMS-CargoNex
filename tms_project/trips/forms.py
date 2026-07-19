from django import forms

from .models import TripExpense


class TripAssignForm(forms.Form):
    builty_id = forms.IntegerField(min_value=1)


class TripExpenseCreateForm(forms.ModelForm):
    class Meta:
        model = TripExpense
        fields = [
            "title",
            "amount",
            "payment_mode",
            "reference_no",
            "expense_date",
            "remarks",
        ]

    def clean_title(self):
        value = (self.cleaned_data.get("title") or "").strip()
        if not value:
            raise forms.ValidationError("Expense title is required.")
        return value

    def clean_reference_no(self):
        value = (self.cleaned_data.get("reference_no") or "").strip()
        return value or None

    def clean_remarks(self):
        value = (self.cleaned_data.get("remarks") or "").strip()
        return value or None


class TripExpenseTitleForm(forms.Form):
    title = forms.CharField(max_length=200)

    def clean_title(self):
        value = (self.cleaned_data.get("title") or "").strip()
        if not value:
            raise forms.ValidationError("Expense title is required.")
        return value
