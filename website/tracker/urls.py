from django.urls import path

from tracker.views import WebsiteDetails


urlpatterns = [
    path('website/<str:website>', WebsiteDetails.as_view(), name='website-details'),
]