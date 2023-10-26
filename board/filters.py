from django_filters import FilterSet
from .models import Reply


class ReplyFilter(FilterSet):
    class Meta:
        model = Reply
        fields = {
            'post',
        }

