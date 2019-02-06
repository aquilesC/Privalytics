from django.contrib import admin

from tracker.models import Tracker

admin.site.register((
    Tracker,
))
