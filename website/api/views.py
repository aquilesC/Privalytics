import time

from ipware.ip import get_real_ip

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializer import TrackerSerializer
from logs.models import TimeToStore


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class TrackerView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    def post(self, request):
        t0 = time.time()
        serializer = TrackerSerializer(data=request.data)
        if serializer.is_valid():
            raw_tracker = serializer.save()
            if not raw_tracker.dnt:
                raw_tracker.ip = get_real_ip(request) or ''
                raw_tracker.user_agent = request.META['HTTP_USER_AGENT']
                raw_tracker.save()
            t1 = time.time()
            TimeToStore.objects.create(measured_time=(t1-t0), measured_type=TimeToStore.POST_RAW_TRACK)
            return Response({'message': 'OK'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


