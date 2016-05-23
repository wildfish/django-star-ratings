from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .app_settings import STAR_RATINGS_RANGE
from .models import Rating, UserRating, AnonymousRating


class UserRatingAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super(UserRatingAdmin, self).get_queryset(request).select_related('rating', 'user').prefetch_related('rating__content_object')

    def stars(self, obj):
        html = "<span style='display: block; width: {}px; height: 10px; " + \
               "background: url(/static/star-ratings/images/admin_stars.png)'>&nbsp;</span>"
        return html.format(obj.score * 10)

    stars.allow_tags = True
    stars.short_description = _('Score')
    list_display = ('__str__', 'stars')

class AnonymousRatingAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super(AnonymousRatingAdmin, self).get_queryset(request).select_related('rating').prefetch_related('rating__content_object')

    def stars(self, obj):
        html = "<span style='display: block; width: {}px; height: 10px; " + \
               "background: url(/static/star-ratings/images/admin_stars.png)'>&nbsp;</span>"
        return html.format(obj.score * 10)

    stars.allow_tags = True
    stars.short_description = _('Score')
    list_display = ('__str__', 'stars')


class RatingAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super(RatingAdmin, self).get_queryset(request).prefetch_related('content_object')

    def stars(self, obj):
        html = "<div style='position: relative;'>"
        html += "<span style='position: absolute; top: 0; left: 0; width: {}px; height: 10px; " + \
                "background: url(/static/star-ratings/images/admin_stars.png) 0px 10px'>&nbsp;</span>"
        html += "<span style='position: absolute; top: 0; left: 0; width: {}px; height: 10px; " + \
                "background: url(/static/star-ratings/images/admin_stars.png)'>&nbsp;</span>"
        html += "</div>"
        return html.format(STAR_RATINGS_RANGE * 10, obj.average * 10)

    stars.allow_tags = True
    stars.short_description = _('Rating average')
    list_display = ('__str__', 'stars')


admin.site.register(Rating, RatingAdmin)
admin.site.register(UserRating, UserRatingAdmin)
admin.site.register(AnonymousRating, AnonymousRatingAdmin)
