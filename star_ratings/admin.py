from django.contrib import admin
from .models import AggregateRating, Rating


class RatingAdmin(admin.ModelAdmin):
    def stars(self, obj):
        html = "<span style='display: block; width: {}px; height: 10px; " + \
               "background: url(/static/star-ratings/images/admin_stars.png)'>&nbsp;</span>"
        return html.format(obj.score * 10)

    stars.allow_tags = True
    stars.short_description = "Score"
    list_display = ('__str__', 'stars')


class AggregateRatingAdmin(admin.ModelAdmin):
    def stars(self, obj):
        html = "<div style='position: relative;'>"
        html += "<span style='position: absolute; top: 0; left: 0; width: {}px; height: 10px; " + \
                "background: url(/static/star-ratings/images/admin_stars.png) 0px 10px'>&nbsp;</span>"
        html += "<span style='position: absolute; top: 0; left: 0; width: {}px; height: 10px; " + \
                "background: url(/static/star-ratings/images/admin_stars.png)'>&nbsp;</span>"
        html += "</div>"
        return html.format(obj.max_value * 10, obj.average * 10)

    stars.allow_tags = True
    stars.short_description = "Rating average"
    list_display = ('__str__', 'stars')


admin.site.register(AggregateRating, AggregateRatingAdmin)
admin.site.register(Rating, RatingAdmin)
