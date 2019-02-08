from django.contrib import admin

from tracker.models import Tracker, Website

admin.site.register((
    Tracker,
    Website,
))
