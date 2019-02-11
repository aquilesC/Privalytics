import logging
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

from django.core.management import BaseCommand, CommandError
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.http import QueryDict
from django.utils.timezone import now

from user_agents import parse as ua_parser
from geoip2.errors import GeoIP2Error

from tracker.models import Tracker, Website

logger = logging.getLogger('tracking_analyzer')


class Command(BaseCommand):
    help = """Parses the logs from a server in order to generate fake data in the database
    """

    def create_from_logs(self, data):
        """ Creates a tracker object from data in logs. It is used just to populate the database with
        real data.
        """
        # First the website:

        website, _ = Website.objects.get_or_create(website_url=data['base_url'])

        user_agent = ua_parser(data.get('useragent'))
        ip_address = data.get('ipaddress')
        location_data = {}

        if not user_agent.is_bot:
            if ip_address:
                geo = GeoIP2()
                try:
                    location_data = geo.city(ip_address)
                except:  # TODO: Check what are the exception that may be risen by GeoIP2. Looks like they have different base exceptions
                    pass

        operating_system = user_agent.os.family
        device_family = user_agent.device.family
        browser = user_agent.browser.family

        if user_agent.is_mobile:
            type_device = Tracker.MOBILE
        elif user_agent.is_tablet:
            type_device = Tracker.TABLET
        elif user_agent.is_pc:
            type_device = Tracker.PC
        elif user_agent.is_bot:
            type_device = Tracker.BOT
        else:
            type_device = Tracker.UNKNOWN

        date = datetime.strptime(data['dateandtime'], '%d/%b/%Y:%H:%M:%S %z')

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

        tracker = Tracker.objects.create(
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
            website=website,
        )
        tracker.timestamp = date
        return tracker

    def add_arguments(self, parser):
        parser.add_argument(
            '--log',
            help='Log file to parse'
        )

        parser.add_argument(
            '--base',
            help='Base url to add to the logs'
        )

    def handle(self, *args, **options):
        filename = options.get('log')
        if not filename:
            raise CommandError('You must specify the log file to parse')

        lineformat = re.compile(
            r"""(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<dateandtime>\d{2}\/[a-z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} (\+|\-)\d{4})\] ((\"(GET|POST) )(?P<url>.+)(http\/1\.1")) (?P<statuscode>\d{3}) (?P<bytessent>\d+) (["](?P<referrer>(\-)|(.+))["]) (["](?P<useragent>.+)["])""",
            re.IGNORECASE)

        with open(filename, 'r') as file:
            t = now()
            i = 0
            for line in file:
                data = re.search(lineformat, line)
                if data:
                    datadict = data.groupdict()
                    status = datadict['statuscode']
                    if status == '200':
                        url = datadict.get('url').strip()
                        if url.endswith('/') or url.endswith('.htm') or url.endswith('.html'):
                            datadict.update({'base_url': options.get('base', '')})
                            tracker = self.create_from_logs(datadict)
                            if tracker:
                                if i==0:
                                    t1 = datetime.strptime(datadict['dateandtime'], '%d/%b/%Y:%H:%M:%S %z')
                                tracker.timestamp = now()-(tracker.timestamp-t1)
                                tracker.save()
                                if tracker.timestamp < now()-timedelta(days=31):
                                    print('Will not go beyond 30 days of data')
                                    break
                                i += 1
                            if i % 20 == 0:
                                print('Parsed {} requests'.format(i), end='\r')
        print('\n')
        print('Finished processing the Logs')