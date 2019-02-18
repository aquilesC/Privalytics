from rest_framework import serializers

from tracker.models import Tracker, Website


class TrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracker
        fields = ('timestamp', 'country', 'region')


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ('website_name', 'website_url', 'monthly_unique')