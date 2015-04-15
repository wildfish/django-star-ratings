from django import template
from ..models import RateableModel

register = template.Library()


@register.inclusion_tag('ratings/widget.html', takes_context=True)
def rating_widget(context, item, star_count=5):
    ratings = RateableModel.objects.ratings_for_item(item)
    stars = [i for i in range(1, star_count+1)]
    request = context.get('request')
    return {
        'ratings': ratings,
        'request': request,
        'user': request.user,
        'stars': stars,
        'star_count': star_count,
        'percentage': 100 / ratings.max_value * ratings.rating_average
    }
