from django.contrib import admin

from tracker.models import Tracker, Website, RawTracker

admin.site.register((
    RawTracker,
    Tracker,
    Website,
))
