from django.db import models
from ..models import RateableModel


class Thing(RateableModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
