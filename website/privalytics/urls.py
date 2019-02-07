from django.contrib import admin
from django.urls import path

from tracker.views import NewTrackView, Index, StatsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tracker', NewTrackView.as_view(), name='New-Tracker'),
    path('', Index.as_view(), name='Index'),
    path('stats', StatsView.as_view(), name='Example-stats'),
]
