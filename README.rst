django-star-ratings
===================

|Build Status| |codecov.io| |Documentation Status|

Python 3 compatible ratings for Django.

Add ratings to any Django model with a template tag.

See full `documentation
<http://django-star-ratings.readthedocs.io/en/latest/?badge=latest/>`_.

Installation
------------

Install from PyPI:

::

    pip install django-star-ratings

add ``star_ratings`` to ``INSTALLED_APPS``:

::

    INSTALLED_APPS = (
        ...
        'star_ratings'
    )

sync your database:

::

    python manage.py migrate

add the following to your urls.py:

::

    url(r'^ratings/', include('star_ratings.urls', namespace='ratings', app_name='ratings')),

Make sure ``'django.core.context_processors.request',`` is in
``TEMPLATE_CONTEXT_PROCESSORS``.

Usage
-----

Add the following javascript and stylesheet to your template

::

    {% load static %}
    <html>
    ...
    <link rel="stylesheet" href="{% static 'star-ratings/css/star-ratings.css' %}">
    <script type="text/javascript" src="{% static 'star-ratings/js/dist/star-ratings.min.js' %}"></script>
    ...
    </html>

To enable ratings for a model add the following tag in your template

::

    {% load ratings %}
    <html>
    ...
    {% ratings object %}
    ...
    </html>

Template tags
-------------

The template tag takes two arguments:

-  ``icon_height``: defaults to ``STAR_RATINGS_STAR_HEIGHT``
-  ``icon_width``: defaults to ``STAR_RATINGS_STAR_WIDTH``
-  ``read_only``: overrides the ``editable`` behaviour to make the widget read only

Settings
--------

To prohibit users from altering their ratings set
``STAR_RATINGS_RERATE = False`` in settings.py

To change the number of rating stars, set ``STAR_RATINGS_RANGE``
(defaults to 5)

To enable anonymous rating set ``STAR_RATINGS_ANONYMOUS = True``.

Anonymous Rating
----------------

If anonymous rating is enabled only the ip address for the rater will be stored (even if the user is logged in).
When a user rates an object a preexisting object will not be searched for, instead a new rating object will be created

**If this value is changed your lookups will return different results!**

To control the default size of stars in pixels set the values of ``STAR_RATINGS_STAR_HEIGHT`` and
``STAR_RATINGS_STAR_WIDTH``. By default ``STAR_RATINGS_STAR_WIDTH`` is the same as
``STAR_RATINGS_STAR_HEIGHT`` and ``STAR_RATINGS_STAR_HEIGHT`` defaults to 32.


Changing the star graphics
--------------------------

To change the star graphic, add a sprite sheet to
``/static/star-ratings/images/stars.png`` with the states aligned
horizontally. The stars should be laid out in three states: full, empty
and active.

Customize widget template
-------------------------

You can customize ratings widget by creating ``star_ratings/widget.html``. For example :

::

    {% extends "star_ratings/widget_base.html" %}
    {% block rating_detail %}
    Whatever you want
    {% endblock %}

See ``star_ratings/widget_base.html`` for other blocks to be extended.

Ordering by ratings
-------------------

The easiest way to order by ratings is to add a ``GenericRelation`` to
the ``Rating`` model from your model:

::

    from django.contrib.contenttypes.fields import GenericRelation
    from star_ratings.models import Rating
    
    class Foo(models.Model):
        bar = models.CharField(max_length=100)
        ratings = GenericRelation(Rating, related_query_name='foos')

    Foo.objects.filter(ratings__isnull=False).order_by('ratings__average')

Running tests
-------------

To run the test use:

::

    $> ./runtests.py

.. |Build Status| image:: https://travis-ci.org/wildfish/django-star-ratings.svg?branch=master
   :target: https://travis-ci.org/wildfish/django-star-ratings
.. |codecov.io| image:: http://codecov.io/github/wildfish/django-star-ratings/coverage.svg?branch=master
   :target: http://codecov.io/github/wildfish/django-star-ratings?branch=master
.. |Documentation Status| image:: https://readthedocs.org/projects/django-star-ratings/badge/?version=latest
   :target: http://django-star-ratings.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. |Docs| :target: https://django-configurations.readthedocs.io/en/latest/
