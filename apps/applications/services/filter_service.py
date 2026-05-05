from typing import Optional

from django.db.models import Q, QuerySet

from ..models import Request


class FilterService:
    @staticmethod
    def apply(
        queryset: QuerySet[Request],
        status: Optional[str] = None,
        category_slug: Optional[str] = None,
        unit_name: Optional[str] = None,
        search: Optional[str] = None,
    ) -> QuerySet[Request]:
        if status:
            queryset = queryset.filter(status=status)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if unit_name:
            queryset = queryset.filter(unit_name__icontains=unit_name)
        if search:
            queryset = queryset.filter(Q(user_name__icontains=search) | Q(phone__icontains=search))
        return queryset
