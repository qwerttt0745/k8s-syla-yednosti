from django.core.exceptions import ValidationError

from ..models import Request


class StatusService:
    ALLOWED_TRANSITIONS = {
        Request.Status.NEW: {Request.Status.IN_PROGRESS, Request.Status.CANCELED},
        Request.Status.IN_PROGRESS: {Request.Status.DONE, Request.Status.CANCELED},
        Request.Status.DONE: set(),
        Request.Status.CANCELED: set(),
    }

    @classmethod
    def update_status(cls, request_obj: Request, new_status: str, user=None) -> Request:
        allowed = cls.ALLOWED_TRANSITIONS.get(request_obj.status, set())
        if new_status not in allowed:
            raise ValidationError("Недопустима зміна статусу")
        request_obj._changed_by = user  # for audit log
        request_obj.status = new_status
        request_obj.save(update_fields=["status", "updated_at"])
        return request_obj

    @classmethod
    def allowed_transitions(cls, request_obj: Request) -> list[str]:
        return list(cls.ALLOWED_TRANSITIONS.get(request_obj.status, set()))
