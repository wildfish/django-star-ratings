from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.edit import CreateView, BaseCreateView, UpdateView
from braces.views import LoginRequiredMixin
from .models import RateableModel


class RatingCreate(LoginRequiredMixin,  UpdateView):
    model = RateableModel
    fields = ['content_type', 'object_id', 'score', ]
    success_url = '/' #TODO

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs[self.pk_url_kwarg])

    def get(self, request, *args, **kwargs):
        return_url = request.GET.get('return')
        value = kwargs['rating_value']

        try:
            ip_address = self.request.META.get('REMOTE_ADDR') or '0.0.0.0'
            self.model.objects.rate(self.get_object(), value, request.user, ip_address)
        except ValidationError as err:
            pass

        if request.is_ajax():
            return JsonResponse(data={'test': 'value'})
        else:
            return HttpResponseRedirect(return_url)

    def form_valid(self, form):
        rating = form.save(commit=False)
        rating.user = self.request.user
        rating.ip_address = self.request.META['REMOTE_ADDR']
        rating.save()
        return HttpResponseRedirect('/')
        #return HttpResponseRedirect(self.get_success_url())
