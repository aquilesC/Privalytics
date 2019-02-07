import json
import time

from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.db.models.functions import TruncDate
from django.db.models import Count

from logs.models import TimeToStore
from tracker.models import Tracker
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
        time_log = TimeToStore(measured_time=t1-t0)
        time_log.save()
        return JsonResponse({'message': 'OK'}, status=200)


class StatsView(View):
    template_name = 'privalytics/dashboard.html'

    def get(self, request, *args, **kwargs):
        extra_context = {}
        countries_count = []

        queryset = Tracker.objects.all()

        trackers = queryset.values('country').annotate(
            trackers=Count('id')).order_by()

        for track in trackers:
            countries_count.append(
                [countries.alpha3(track['country']), track['trackers']])

        extra_context['countries_count'] = json.dumps(countries_count)

        # current_results = queryset.annotate(
        #     date=TruncDate('timestamp'),
        #     hour=Extract('timestamp', 'hour'),
        #     minute=Extract('timestamp', 'minute')
        # ).values('date', 'hour', 'minute'
        #          ).annotate(requests=Count('pk', 'date'))

        current_results = queryset.annotate(
            date=TruncDate('timestamp'),
        ).values('date'
                 ).annotate(requests=Count('pk', 'date'))

        for item in current_results:
            item['date'] = '{date}'.format(
                date=item.pop('date')
            )

        extra_context['requests_count'] = json.dumps(list(current_results))

        devices_count = list(queryset.exclude(type_device__exact=Tracker.UNKNOWN).values('type_device').annotate(
            count=Count('id')).order_by('-count'))[:10]

        for dev in devices_count:
            dev['type_device'] = Tracker.DEVICE_CHOICES[dev['type_device']][1]

        extra_context['devices_count'] = json.dumps(devices_count)

        top_pages = Tracker.objects.all().values('page').annotate(total=Count('page')).order_by('-total')[:10]
        extra_context['top_pages'] = top_pages

        return render(request, self.template_name, extra_context)