import json

from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from tracker.models import Tracker


class NewTrackView(View):
    """ This view is responsible for adding the new track event into the database
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(NewTrackView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        track = Tracker.create_from_json(request, data)
        track.save()
        return JsonResponse({'message': 'OK'}, status=200)

