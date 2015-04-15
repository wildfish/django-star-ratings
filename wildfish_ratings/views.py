from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.edit import CreateView, BaseCreateView, UpdateView
from braces.views import LoginRequiredMixin
from .models import RateableModel


class RatingCreate(LoginRequiredMixin,  UpdateView):
    model = RateableModel

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs[self.pk_url_kwarg])

    def get(self, request, *args, **kwargs):
        return_url = request.GET.get('return') or '/'
        value = kwargs['rating_value']
        try:
            ip_address = self.request.META.get('REMOTE_ADDR') or '0.0.0.0'
            rated_model = self.model.objects.rate(self.get_object(), value, request.user, ip_address)
            if request.is_ajax():
                return JsonResponse(data=rated_model.to_dict(), status=200)
            else:
                return HttpResponseRedirect(return_url)
        except ValidationError as err:
            if request.is_ajax():
                return JsonResponse(data={'error': 'error message here'})
            else:
                return HttpResponseRedirect(return_url)
