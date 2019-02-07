import json
import time

from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from logs.models import TimeToStore
from tracker.models import Tracker


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

