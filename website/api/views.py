import json
import time

from ipware.ip import get_real_ip
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Profile
from api.serializer import TrackerSerializer
from logs.models import TimeToStore
from tracker.models import Tracker


class TrackerView(APIView):
    def post(self, request):
        serializer = TrackerSerializer(data=request.data)
        if serializer.is_valid():
            raw_tracker = serializer.save()
            if not raw_tracker.dnt:
                raw_tracker.ip = get_real_ip(request) or ''
                raw_tracker.user_agent = request.META['HTTP_USER_AGENT']
                raw_tracker.save()
            return Response({'message': 'OK'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
