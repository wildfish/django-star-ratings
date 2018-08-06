from __future__ import absolute_import
from django import forms

from . import get_star_ratings_rating_model
from .models import UserRating


class CreateUserRatingForm(forms.ModelForm):
    class Meta:
        model = UserRating
        exclude = [
            'count',
            'total',
            'average',
            'rating',
        ]

    def __init__(self, obj=None, *args, **kwargs):
        self.obj = obj
        super(CreateUserRatingForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        return get_star_ratings_rating_model().objects.rate(
            self.obj,
            self.cleaned_data['score'],
            user=self.cleaned_data['user'],
            ip=self.cleaned_data['ip']
        )
