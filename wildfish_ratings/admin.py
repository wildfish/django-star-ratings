from django.contrib import admin
from .models import RateableModel, Rating


class RatingAdmin(admin.ModelAdmin):
    def stars(self, obj):
        return "&#9733" * obj.score

    stars.allow_tags = True
    stars.short_description = "Score"
    list_display = ('__str__', 'stars')


class RateableModelAdmin(admin.ModelAdmin):
    def stars(self, obj):
        return "&#9733" * obj.rating_average + "&#9734" * (obj.max_value - obj.rating_average)

    stars.allow_tags = True
    stars.short_description = "Rating average"
    list_display = ('__str__', 'stars')


admin.site.register(RateableModel, RateableModelAdmin)
admin.site.register(Rating, RatingAdmin)
