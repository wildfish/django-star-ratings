from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View
from braces.views import LoginRequiredMixin
from .models import Rating
import json


class Rate(LoginRequiredMixin, View):
    model = Rating

    def get_object(self):
        """
        Returns the model instance we're rating from the URL params.
        """
        content_type = ContentType.objects.get_for_id(self.kwargs.get('content_type_id'))
        return content_type.get_object_for_this_type(pk=self.kwargs.get('object_id'))

    def post(self, request, *args, **kwargs):
        return_url = request.GET.get('next', '/')
        ip = self.request.META.get('REMOTE_ADDR') or '0.0.0.0'
        data = json.loads(request.body.decode())
        score = data.get('score')
        try:
            rating = self.model.objects.rate(self.get_object(), score, request.user, ip)
            if request.is_ajax():
                result = rating.to_dict()
                result['user_rating'] = int(score)
                return JsonResponse(data=result, status=200)
            else:
                return HttpResponseRedirect(return_url)
        except ValidationError as err:
            if request.is_ajax():
                return JsonResponse(data={'error': err.message}, status=400)
            else:
                return HttpResponseRedirect(return_url)
