from django import forms

from .models import Purchase


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["actual_cost", "purchase_date", "funding_source", "receipt_photo"]
        widgets = {
            "actual_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "15000.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "purchase_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "funding_source": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Загальний збір / Цільовий донат",
                }
            ),
            "receipt_photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }
        labels = {
            "actual_cost": "Фактична вартість (грн)",
            "purchase_date": "Дата чеку",
            "funding_source": "Джерело фінансування",
            "receipt_photo": "Фото чеку",
        }


class ReportFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
