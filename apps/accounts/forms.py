from django import forms

from .models import CustomUser


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "volunteer@example.com"}
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class VolunteerCreateForm(forms.ModelForm):
    """Form for creating a new volunteer by a director."""

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Мінімум 8 символів"}
        ),
        min_length=8,
    )
    password_confirm = forms.CharField(
        label="Підтвердження пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = CustomUser
        fields = ["email", "role"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "volunteer@syla.ua"}
            ),
            "role": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "email": "Email",
            "role": "Роль",
        }

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        password_confirm = cleaned.get("password_confirm")
        email = cleaned.get("email")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Паролі не співпадають")
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач з таким email вже існує")
        return cleaned
