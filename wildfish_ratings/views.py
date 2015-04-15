from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.edit import CreateView
from braces.views import LoginRequiredMixin
from .models import Rating


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class RatingCreate(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    model = Rating
    fields = ['content_type', 'object_id', 'score', ]
    success_url = '/'  # TODO

    def form_valid(self, form):
        rating = form.save(commit=False)
        rating.user = self.request.user
        rating.ip_address = self.request.META['REMOTE_ADDR']
        rating.save()
        return HttpResponseRedirect('/')
        # return HttpResponseRedirect(self.get_success_url())
