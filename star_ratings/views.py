from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from braces.views import LoginRequiredMixin
from .models import AggregateRating


class RatingCreate(LoginRequiredMixin, SingleObjectMixin, View):
    model = AggregateRating

    def post(self, request, *args, **kwargs):
        return_url = request.GET.get('next', '/')
        score = kwargs['score']
        try:
            ip = self.request.META.get('REMOTE_ADDR') or '0.0.0.0'
            rated_model = self.model.objects.rate(self.get_object(), score, request.user, ip)
            if request.is_ajax():
                return JsonResponse(data=rated_model.to_dict(), status=200)
            else:
                return HttpResponseRedirect(return_url)
        except ValidationError as err:
            if request.is_ajax():
                return JsonResponse(data={'error': err.message}, status=400)
            else:
                return HttpResponseRedirect(return_url)
