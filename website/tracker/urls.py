from django.urls import path

from tracker.views import WebsiteStats

urlpatterns = [
    path('stats/<str:website_url>', WebsiteStats.as_view(), name='website')
]