from django.contrib import admin

from . import models

admin.site.register(models.Diet)
admin.site.register(models.Period)
admin.site.register(models.Location)
admin.site.register(models.Taxon)
admin.site.register(models.Dinosaur)
