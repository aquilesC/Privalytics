import json
import time
from collections import Counter

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic import TemplateView, DetailView
from django.db.models.functions import TruncDate, Extract, TruncHour
from django.db.models import Count

from logs.models import TimeToStore
from tracker.models import Tracker, Website
from django_countries import countries


class Index(TemplateView):
    template_name = 'privalytics/index.html'


class NewTrackView(View):
    """ This view is responsible for adding the new track event into the database
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(NewTrackView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        t0 = time.time()
        data = json.loads(request.body)
        track = Tracker.create_from_json(request, data)
        track.save()
        t1 = time.time()
        time_log = TimeToStore(measured_time=t1 - t0)
        time_log.save()
        return JsonResponse({'message': 'OK'}, status=200)


class WebsiteDetails(DetailView):
    model = Website
    template_name = 'accounts/bar-charts.html'
    context_object_name = 'website'

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Website, website_url=self.kwargs.get('website_url'))
