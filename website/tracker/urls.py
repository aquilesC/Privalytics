from django.urls import path

from tracker.views import WebsiteStats

urlpatterns = [
    path('ws/<str:website_url>', WebsiteStats.as_view(), name='website')
]