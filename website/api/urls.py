from django.urls import path

from api.views import TrackerView

urlpatterns = [
    path('tracker', TrackerView.as_view(), name='tracker-api'),
]
