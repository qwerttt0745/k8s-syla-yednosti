from apps.applications.models import Request


ALLOWED_TRANSITIONS = {
    Request.Status.NEW: [Request.Status.IN_PROGRESS, Request.Status.CANCELED],
    Request.Status.IN_PROGRESS: [Request.Status.DONE, Request.Status.CANCELED],
    Request.Status.DONE: [],
    Request.Status.CANCELED: [],
}


class StatusService:
    ALLOWED_TRANSITIONS = ALLOWED_TRANSITIONS

    @staticmethod
    def can_transition(request_obj: Request, new_status: str) -> bool:
        return new_status in ALLOWED_TRANSITIONS.get(request_obj.status, [])

    @staticmethod
    def transition(request_obj: Request, new_status: str, changed_by) -> bool:
        if not StatusService.can_transition(request_obj, new_status):
            return False

        if new_status == Request.Status.IN_PROGRESS:
            request_obj.assigned_to = changed_by

        if new_status == Request.Status.DONE and not request_obj.assigned_to:
            request_obj.assigned_to = changed_by

        request_obj._changed_by = changed_by
        request_obj.status = new_status
        request_obj.save()
        return True

    @staticmethod
    def allowed_transitions(request_obj: Request) -> list[str]:
        return list(ALLOWED_TRANSITIONS.get(request_obj.status, []))
