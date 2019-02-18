from rest_framework import viewsets

from tracker.models import Website
from tracker.serializers import WebsiteSerializer


class WebsiteApiView(viewsets.ModelViewSet):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer