import uuid
from django import template
from ..models import AggregateRating
from .. import app_settings

register = template.Library()

@register.inclusion_tag('ratings/widget.html', takes_context=True)
def ratings(context, item, icon_height=32, icon_width=32, star_count=None):
    if not star_count:
        star_count = app_settings.STAR_RATINGS_RANGE
    rating = AggregateRating.objects.ratings_for_item(item)
    stars = [i for i in range(1, star_count + 1)]
    request = context.get('request')

    if request is None:
        raise Exception('Make sure you have "django.core.context_processors.request" in "TEMPLATE_CONTEXT_PROCESSORS"')

    return {
        'rating': rating,
        'request': request,
        'user': request.user,
        'stars': stars,
        'star_count': star_count,
        'percentage': 100 / rating.max_value * rating.rating_average,
        'icon_height': icon_height,
        'icon_width': icon_width,
        'id': 'wfr{}'.format(uuid.uuid4().hex)
    }
