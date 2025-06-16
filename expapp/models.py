from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField

class Country(models.Model):
    name_common = models.CharField(max_length=100, unique=True)
    name_official = models.CharField(max_length=200)
    capital = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    population = models.BigIntegerField()
    area = models.FloatField()
    languages = JSONField(default=dict)
    region = models.CharField(max_length=50, blank=True)
    subregion = models.CharField(max_length=100, blank=True)
    currencies = JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_common

