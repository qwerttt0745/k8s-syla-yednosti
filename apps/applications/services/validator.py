import re

from django.core.exceptions import ValidationError


class RequestValidator:
    PHONE_REGEX = re.compile(r"^\+380\d{9}$")

    @classmethod
    def validate_phone(cls, phone: str) -> None:
        if not cls.PHONE_REGEX.match(phone):
            raise ValidationError("Невірний формат телефону")
