from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.inclusion_tag('ratings/widget.html', takes_context=True)
def rating_widget(context, item):
    return {'object': item,
            'content_type_id': ContentType.objects.get_for_model(item).pk,
            'user': context['user']}
