from django.contrib import admin
from django.urls import path

from tracker.views import NewTrackView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tracker', NewTrackView.as_view(), name='New-Tracker'),
]
