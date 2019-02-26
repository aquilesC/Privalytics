from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from api.views import TrackerView

urlpatterns = [
    path('tracker', csrf_exempt(TrackerView.as_view()), name='tracker-api'),
]
