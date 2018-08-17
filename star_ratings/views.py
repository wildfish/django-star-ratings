from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View

from . import app_settings, get_star_ratings_rating_model
from .forms import CreateUserRatingForm
from .compat import is_authenticated
import json


class Rate(View):
    model = get_star_ratings_rating_model()

    def get_object(self):
        """
        Returns the model instance we're rating from the URL params.
        """
        content_type = ContentType.objects.get_for_id(self.kwargs.get('content_type_id'))
        return content_type.get_object_for_this_type(pk=self.kwargs.get('object_id'))

    def post(self, request, *args, **kwargs):
        def _post(request, *args, **kwargs):
            data = request.POST or json.loads(request.body.decode())

            return_url = data.pop('next', '/')
            if 'HTTP_X_REAL_IP' in self.request.META:
                data['ip'] = self.request.META['HTTP_X_REAL_IP']
            else:
                data['ip'] = self.request.META['REMOTE_ADDR']

            data['user'] = is_authenticated(request.user) and request.user.pk or None

            if not request.session or not request.session.session_key:
                request.session.save()

            data['session'] = self.request.session.session_key

            res_status = 200

            try:
                form = CreateUserRatingForm(data=data, obj=self.get_object())
                if form.is_valid():
                    rating = form.save()
                    result = rating.to_dict()
                    result['user_rating'] = int(form.cleaned_data['score'])
                else:
                    result = {'errors': form.errors}
                    res_status = 400
            except ValidationError as err:
                result = {'errors': err.message}
                res_status = 400

            if request.is_ajax():
                return JsonResponse(data=result, status=res_status)
            else:
                return HttpResponseRedirect(return_url)

        if not app_settings.STAR_RATINGS_ANONYMOUS:
            return login_required(_post)(request, *args, **kwargs)

        return _post(request, *args, **kwargs)
