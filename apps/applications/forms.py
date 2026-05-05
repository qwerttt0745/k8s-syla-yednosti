from django import forms

from .models import Comment, Request
from .services.validator import RequestValidator


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = [
            "user_name",
            "phone",
            "unit_name",
            "category",
            "priority",
            "item_name",
            "quantity",
            "location",
            "post_dept",
        ]
        widgets = {
            "user_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+380"}),
            "unit_name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "item_name": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "post_dept": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        RequestValidator.validate_phone(phone)
        return phone


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 3, "class": "form-control"})}
