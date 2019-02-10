from django.contrib import admin
from django.urls import path, include


from tracker.views import NewTrackView, Index, StatsView, BaseChart

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tracker', NewTrackView.as_view(), name='New-Tracker'),
    path('', Index.as_view(), name='index'),
    path('stats', StatsView.as_view(), name='example-stats'),
    path('base_stats', BaseChart.as_view(), name='base-chart'),
    path('', include('accounts.urls')),
]
