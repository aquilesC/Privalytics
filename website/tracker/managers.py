from datetime import datetime
import logging
import time

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.db import models
from django.http import QueryDict
from django_user_agents.utils import get_user_agent
from ua_parser import user_agent_parser
from user_agents import parse as ua_parser
from urllib.parse import urlparse
from geoip2.errors import GeoIP2Error
from ipware.ip import get_real_ip


logger = logging.getLogger('tracking_analyzer')


class TrackerManager(models.Manager):
    """ Tracker manager that is able to create a new Tracker object based on a request and
    data in dictionary format.
    """

    def create_from_logs(self, data):
        """ Creates a tracker object from data in logs. It is used just to populate the database with
        real data.
        """
        parsed_ua = ua_parser(data['useragent'])
        if not parsed_ua.is_bot:
            date = datetime.strptime(data['dateandtime'], '%d/%b/%Y:%H:%M:%S %z')
            # timestamp = time.mktime(date.timetuple())
            ip_address = data['ipaddress']
            city = {}
            geo = GeoIP2()
            try:
                city = geo.city(ip_address)
            except (GeoIP2Error, GeoIP2Exception):
                logger.exception(
                    'Unable to determine geolocation for address %s', ip_address)

            parsed_string = user_agent_parser.Parse(data['useragent'])
            device = parsed_string['device']
            op_system = parsed_string['os']
            browser = parsed_string['user_agent']

            parsed_url = urlparse(data['base_url'] + data['url'])
            queries = QueryDict(parsed_url.query, mutable=False)

            url = parsed_url.hostname
            page = parsed_url.path
            utm_source = queries.get('utm_source')

            parsed_referrer = urlparse(data['referrer'])
            referrer_url = parsed_referrer.hostname
            referrer_page = parsed_referrer.path

            tracker = self.model.objects.create(
                ip_address=ip_address,
                country=city.get('country_code', '') or '',
                ip_region=city.get('region', '') or '',
                ip_city=city.get('city', '') or '',

                device_brand=device.get('brand', '') or '',
                device_family=device.get('family', '') or '',
                browser=browser.get('family', '') or '',
                browser_version=browser.get('major', '') or '',
                system=op_system.get('family', '') or '',
                system_version=op_system.get('major', '') or '',

                url=url or '',
                page=page or '',
                utm_source=utm_source,

                screen_width=int(data.get('width', 0)),

                referrer_url=referrer_url,
                referrer_page=referrer_page,
            )
            tracker.timestamp = date
            tracker.save()
            return tracker

    def create_from_json(self, request, data):
        """ This is aimed at data originating from a POST request.

        :param data: Json-formatted information, originating from a javascript installed on
        someone's website.
        """
        # Get the IP address and so the geographical info, if available.
        ip_address = get_real_ip(request) or ''
        user_agent = get_user_agent(request)

        city = {}
        if not ip_address:
            logger.debug(
                'Could not determine IP address for request %s', request)
        else:
            geo = GeoIP2()
            try:
                city = geo.city(ip_address)
            except (GeoIP2Error, GeoIP2Exception):
                logger.exception(
                    'Unable to determine geolocation for address %s', ip_address)

        operating_system = user_agent.os.family
        device_family = user_agent.device.family



        op_system = parsed_string['os']
        browser = parsed_string['user_agent']

        parsed_url = urlparse(data['url'])
        queries = QueryDict(parsed_url.query, mutable=False)

        url = parsed_url.hostname
        page = parsed_url.path
        utm_source = queries.get('utm_source')

        parsed_referrer = urlparse(data['referrer'])
        referrer_url = parsed_referrer.hostname
        referrer_page = parsed_referrer.path

        tracker = self.model.objects.create(
            country=city.get('country_code', '') or '',
            ip_region=city.get('region', '') or '',
            ip_city=city.get('city', '') or '',

            device_brand=device_brand.get('brand', '') or '',
            device_family=device_brand.get('family', '') or '',
            browser=browser.get('family', '') or '',
            browser_version=browser.get('major', '') or '',
            system=op_system.get('family', '') or '',
            system_version=op_system.get('major', '') or '',

            url=url or '',
            page=page or '',
            utm_source=utm_source,

            screen_width=int(data.get('width', 0)),

            referrer_url=referrer_url,
            referrer_page=referrer_page,
        )

        return tracker

