import json
import time

from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Profile
from logs.models import TimeToStore
from tracker.models import Tracker


class TrackerView(APIView):

    def post(self, request):
        t0 = time.time()
        data = json.loads(request.body)
        account_id = data.get('account_id')

        if not Profile.objects.filter(account_id=account_id).exists():
            return Response({'message': 'wrong account id'}, status=403)

        track = Tracker.create_from_json(request, data)
        track.save()
        t1 = time.time()
        time_log = TimeToStore(measured_time=t1 - t0)
        time_log.save()
        return Response({'message': 'OK'}, status=200)