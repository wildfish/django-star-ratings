# django-star-ratings

[![Build Status](https://travis-ci.org/wildfish/django-star-ratings.svg)](https://travis-ci.org/wildfish/django-star-ratings)
[![codecov.io](http://codecov.io/github/wildfish/django-star-ratings/coverage.svg?branch=master)](http://codecov.io/github/wildfish/django-star-ratings?branch=master)

Add ratings to any model with a template tag.


## Installation

`pip install django-star-ratings`

add `star_ratings` to `INSTALLED_APPS`

    INSTALLED_APPS = (
        ...
        'star_ratings'
    )

add the following to your urls.py:

    url(r'^ratings/', include('star_ratings.urls', namespace='ratings', app_name='ratings')),


Make sure `'django.core.context_processors.request',` is in `TEMPLATE_CONTEXT_PROCESSORS`.


## Running Tests

To run the test first install tox using:

```
$> pip install tox
```

Then to run the tests use:
 
```
$> tox
```


## Usage

Add the following javascript and stylesheet to you template
    
    {% load static %}
    <html>
    ...
    <link rel="stylesheet" href="{% static 'star-ratings/css/star-ratings.css' %}">
    <script type="text/javascript" src="{% static 'star-ratings/js/dist/star-ratings.min.js' %}"></script>
    ...
    </html>


To enable ratings for a model add the following tag in your template

    {% load ratings %}
    <html>
    ...
    {% ratings object %}
    ...
    </html>
    
    
## Settings

To prohibit users from altering their ratings set `STAR_RATINGS_RERATE = False` in settings.py


## Template tags

The template tag takes three arguments:

*  `icon_height`: defaults to 32
*  `icon_width`: defaults to 32 
*  `star_count`: defaults to 5. This is the max rating (this means a value between 1 and 5)

To set a rating between 1 and 10 with an icon size of 16px: `{% ratings object 16 16 10 %}`


## Changing the star graphics

To change the star graphic, add a sprite sheet to `/static/star-ratings/images/stars.png` with the states aligned horizontally.
The stars should be laid out in three states: full, empty and active.


## Ordering by ratings

The easiest way to order by ratings is to add a `GenericRelation` to the `AggregateRating` model from your model:


    class Foo(models.Model):
        bar = models.CharField(max_length=100)
        ratings = GenericRelation(AggregateRating, related_query_name='foos')

    Foo.objects.filter(ratings__isnull=False).order_by('ratings__average')
