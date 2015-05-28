from django.contrib import admin
from .models import RateableModel, Rating


admin.site.register(RateableModel)
admin.site.register(Rating)
