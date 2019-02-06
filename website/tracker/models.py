from django.db import models
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.http import QueryDict

from urllib.parse import urlparse
from ipware.ip import get_real_ip
from django_countries.fields import CountryField
from django_user_agents.utils import get_user_agent


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
    # The page visited (everything after the first '/')
    page = models.CharField(max_length=255, blank=True)
    # Query arguments, such as utm_source
    # TODO: Find out what arguments are important for users
    utm_source = models.CharField(max_length=255, null=True)

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

        parsed_referrer = urlparse(data['referrer'])
        referrer_url = parsed_referrer.hostname
        referrer_page = parsed_referrer.path


        tracker = cls(
            country=location_data.get('country_code', '') or '',
            region=location_data.get('region', '') or '',
            city=location_data.get('city', '') or '',

            type_device=type_device,

            operating_system = operating_system,
            device_family=device_family,
            browser=browser,

            url=url or '',
            page=page or '',
            utm_source=utm_source,

            screen_width=int(data.get('width', 0)),
            screen_height=int(data.get('height', 0)),
            referrer_url=referrer_url or None,
            referrer_page=referrer_page or None,
        )

        return tracker

    def __str__(self):
        return "Tracker {} on page {}{}".format(self.pk, self.url, self.page)
