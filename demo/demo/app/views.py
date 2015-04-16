from django.views.generic import DetailView
from .models import Foo


class FooView(DetailView):
    model = Foo

    def get_object(self, queryset=None):
        obj, created = self.model.objects.get_or_create(bar='foo bar baz')
        return obj
