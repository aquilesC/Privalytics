import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.db.models import Count
from django.db.models.functions import TruncHour, TruncDay, TruncMonth
from django.http import QueryDict

from urllib.parse import urlparse

from django.utils.timezone import now
from ipware.ip import get_real_ip
from django_countries.fields import CountryField
from django_user_agents.utils import get_user_agent
from django_countries import countries


class Website(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    website_url = models.URLField(unique=True)

    @property
    def visits_hour(self):
        """Calculates visits per hour in the last 48 hours.
        TODO: It should limit the time range that it generates
        """

        current_results = self.trackers \
            .filter(timestamp__gte=now() - timedelta(days=2)) \
            .annotate(hour=TruncHour('timestamp')) \
            .values('hour') \
            .annotate(requests=Count('pk')).order_by('-hour')

        for item in current_results:
            item['t'] = '{date}' \
                .format(date=item.pop('hour'))
            item['y'] = item.pop('requests')

        return json.dumps(list(current_results))

    @property
    def visits_day(self):
        """Calculates visits per day in the last 30 days.
        TODO: It should limit the time range that it generates
        """

        current_results = self.trackers \
            .filter(timestamp__gte=now() - timedelta(days=30)) \
            .exclude(type_device=Tracker.BOT) \
            .exclude(referrer_url__contains=self.website_url)\
            .annotate(day=TruncDay('timestamp')) \
            .values('day') \
            .annotate(requests=Count('pk')).order_by('-day')

        for item in current_results:
            item['t'] = '{date}' \
                .format(date=item.pop('day'))
            item['y'] = item.pop('requests')

        return json.dumps(list(current_results))

    @property
    def visits_month(self):
        """ Calculates the number of visits per month. In the last year.
        """

        current_results = self.trackers \
            .filter(timestamp__gte=now() - timedelta(days=365)) \
            .exclude(type_device=Tracker.BOT) \
            .annotate(month=TruncMonth('timestamp')) \
            .values('month') \
            .annotate(requests=Count('pk')).order_by('-month')

        for item in current_results:
            item['t'] = '{date}' \
                .format(date=item.pop('month'))
            item['y'] = item.pop('requests')

        return json.dumps(list(current_results))

    @property
    def popular_pages_30_days(self):
        pages = self.trackers \
                    .filter(timestamp__gte=now() - timedelta(days=30)) \
                    .exclude(type_device=Tracker.BOT) \
                    .values('page') \
                    .annotate(visits=Count('page')) \
                    .order_by('-visits')[:20]

        return pages


    @property
    def top_referrers_30_days(self):
        referrers = self.trackers.exclude(referrer_url='') \
                        .filter(timestamp__gte=now() - timedelta(days=30)) \
                        .exclude(referrer_url__contains=self.website_url) \
                        .values('referrer_url') \
                        .annotate(visits=Count('referrer_url')) \
                        .order_by('-visits')[:10]

        return referrers


    @property
    def countries_30_days(self):
        trackers = self.trackers \
            .filter(timestamp__gte=now() - timedelta(days=30)) \
            .exclude(country='') \
            .values('country') \
            .annotate(trackers=Count('id')) \
            .order_by()

        countries_count = []
        for track in trackers:
            countries_count.append(
                [countries.alpha3(track['country']), track['trackers']])

        return json.dumps(countries_count)


    @property
    def popular_devices_30_days(self):
        trackers = self.trackers \
            .filter(timestamp__gte=now() - timedelta(days=30)) \
            .exclude(type_device=Tracker.BOT) \
            .exclude(type_device=Tracker.UNKNOWN) \
            .values('type_device') \
            .annotate(number=Count('id')) \
            .order_by('-number')

        visits_list = []
        devices_list = []
        for tracker in trackers:
            devices_list.append(Tracker.DEVICE_CHOICES[tracker['type_device'] - 1][1])
            visits_list.append(tracker['number'])
        return json.dumps({'device_label': devices_list, 'visits_data': visits_list})


    def __str__(self):
        return "Website: <{}>".format(self.website_url)


class Tracker(models.Model):
    """Each Tracker object corresponds to a different request sent to the server.
    The amount of parameters logged has to be carefully designed.
    """
    MOBILE = 1
    TABLET = 2
    PC = 3
    BOT = 4
    UNKNOWN = 5

    DEVICE_CHOICES = (
        (MOBILE, 'mobile'),
        (TABLET, 'tablet'),
        (PC, 'pc'),
        (BOT, 'bot'),
        (UNKNOWN, 'unknown')
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    country = CountryField()
    region = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)

    type_device = models.IntegerField(choices=DEVICE_CHOICES, default=UNKNOWN)

    operating_system = models.CharField(max_length=255, blank=True)
    device_family = models.CharField(max_length=255, blank=True)
    browser = models.CharField(max_length=255, blank=True)

    # The domain of the request (everything up to the first '/')
    url = models.URLField()
    website = models.ForeignKey(Website, on_delete=models.CASCADE, to_field='website_url',
                                default='pythonforthelab.com', null=True, related_name='trackers')
    # The page visited (everything after the first '/')
    page = models.CharField(max_length=255, blank=True)
    # Query arguments, such as utm_source
    # TODO: Find out what arguments are important for users
    utm_source = models.CharField(max_length=255, null=True, blank=True)

    screen_height = models.IntegerField(null=True)
    screen_width = models.IntegerField(null=True)

    # The domain of the referrer, everything up to the first '/'
    referrer_url = models.URLField(blank=True, null=True)
    # The page from which the visitor came from. Everything from the first '/'
    referrer_page = models.CharField(max_length=255, blank=True, null=True)

    @classmethod
    def create_from_json(cls, request, data):
        """ This is aimed at data originating from a POST request.

        :param data: Json-formatted information, originating from a javascript installed on
        someone's website.
        """

        # Get the IP address and so the geographical info, if available.
        ip_address = get_real_ip(request) or ''
        user_agent = get_user_agent(request)

        location_data = {}
        # Get location only for non-bots:
        if not user_agent.is_bot:
            if ip_address:
                geo = GeoIP2()
                try:
                    location_data = geo.city(ip_address)
                except GeoIP2Exception:
                    pass

        operating_system = user_agent.os.family
        device_family = user_agent.device.family
        browser = user_agent.browser.family

        if user_agent.is_mobile:
            type_device = cls.MOBILE
        elif user_agent.is_tablet:
            type_device = cls.TABLET
        elif user_agent.is_pc:
            type_device = cls.PC
        elif user_agent.is_bot:
            type_device = cls.BOT
        else:
            type_device = cls.UNKNOWN

        parsed_url = urlparse(data['url'])
        queries = QueryDict(parsed_url.query, mutable=False)

        url = parsed_url.hostname
        page = parsed_url.path
        utm_source = queries.get('utm_source')

        referrer_url = None
        referrer_page = None
        if data.get('referrer'):
            parsed_referrer = urlparse(data['referrer'])
            referrer_url = parsed_referrer.hostname
            referrer_page = parsed_referrer.path

        tracker = cls(
            country=location_data.get('country_code', '') or '',
            region=location_data.get('region', '') or '',
            city=location_data.get('city', '') or '',

            type_device=type_device,

            operating_system=operating_system,
            device_family=device_family,
            browser=browser,

            url=url or '',
            page=page or '',
            utm_source=utm_source,

            screen_width=int(data.get('width', 0)),
            screen_height=int(data.get('height', 0)),
            referrer_url=referrer_url,
            referrer_page=referrer_page,
        )

        return tracker

    def __str__(self):
        return "Tracker {} on page {}{}".format(self.get_type_device_display(), self.url, self.page)
