from django.contrib import admin
from django.urls import path, include


from tracker.views import NewTrackView, Index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tracker', NewTrackView.as_view(), name='New-Tracker'),
    path('', Index.as_view(), name='index'),
    path('', include('accounts.urls')),
]
