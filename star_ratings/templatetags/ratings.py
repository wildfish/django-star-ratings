from decimal import Decimal
import uuid
from django import template
from ..models import Rating, UserRating
from ..app_settings import STAR_RATINGS_RANGE

register = template.Library()


@register.inclusion_tag('star_ratings/widget.html', takes_context=True)
def ratings(context, item, icon_height=32, icon_width=32):
    request = context.get('request')

    if request is None:
        raise Exception('Make sure you have "django.core.context_processors.request" in "TEMPLATE_CONTEXT_PROCESSORS"')

    rating = Rating.objects.for_instance(item)
    if request.user.is_authenticated():
        user_rating = UserRating.objects.for_instance_by_user(item, request.user)
    else:
        user_rating = None

    stars = [i for i in range(1, STAR_RATINGS_RANGE + 1)]

    return {
        'rating': rating,
        'request': request,
        'user': request.user,
        'user_rating': user_rating,
        'stars': stars,
        'star_count': STAR_RATINGS_RANGE,
        'percentage': 100 * (rating.average / Decimal(STAR_RATINGS_RANGE)),
        'icon_height': icon_height,
        'icon_width': icon_width,
        'id': 'dsr{}'.format(uuid.uuid4().hex)
    }
