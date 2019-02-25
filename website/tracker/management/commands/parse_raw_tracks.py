import time

from django.core.management import BaseCommand

from accounts.models import Profile
from tracker.models import RawTracker, Tracker, Website
from urllib.parse import urlparse
from django.http import QueryDict
from user_agents import parse
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Checkes the raw logs and generates final trackers based on them
    """

    def handle(self, *args, **options):
        t0 = time.time()
        raw_trackers = RawTracker.objects.filter(processed=False)
        logger.info('Going to process {} raw tracks'.format(raw_trackers.count()))
        for raw_tracker in raw_trackers:
            # Let's verify account:
            try:
                profile = Profile.objects.get(account_id=raw_tracker.account_id)
            except Profile.DoesNotExist:
                # raw_tracker.ip = None
                raw_tracker.wrong_account_id = True
                raw_tracker.processed = True
                raw_tracker.save()
                continue
            parsed_url = urlparse(raw_tracker.url)
            queries = QueryDict(parsed_url.query, mutable=False)
            url = parsed_url.hostname
            page = parsed_url.path
            utm_source = queries.get('utm_source')
            website_url = url.lower()
            website_url = website_url.replace('http://', '').replace('https://', '').replace('www.', '')
            try:
                website = Website.objects.get(website_url=website_url)
            except Website.DoesNotExist:
                # raw_tracker.ip = None
                raw_tracker.website_does_not_exist = True
                raw_tracker.processed = True
                raw_tracker.save()
                continue

            if website.owner != profile.user:
                # raw_tracker.ip = None
                raw_tracker.wrong_owner = True
                raw_tracker.processed = True
                raw_tracker.save()

            referrer_url = None
            referrer_page = None
            if raw_tracker.referrer:
                parsed_referrer = urlparse(raw_tracker.referrer)
                referrer_url = parsed_referrer.hostname
                referrer_page = parsed_referrer.path

            tracker = Tracker.objects.create(
                url=url,
                page=page,
                website=website,
                referrer_url=referrer_url,
                referrer_page=referrer_page,
                timestamp=raw_tracker.timestamp,
                utm_source=utm_source,
            )

            if not raw_tracker.dnt:
                user_agent = parse(raw_tracker.user_agent)
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

                tracker.screen_height = raw_tracker.screen_height
                tracker.screen_width = raw_tracker.screen_width

                tracker.operating_system = operating_system
                tracker.device_family = device_family
                tracker.browser = browser
                tracker.type_device = type_device

                tracker.save()

                if profile.can_geolocation and not user_agent.is_bot:
                    if raw_tracker.ip:
                        geo = GeoIP2()
                        try:
                            location_data = geo.city(raw_tracker.ip)
                            tracker.country = location_data.get('country_code', '') or ''
                            tracker.region = location_data.get('region', '') or ''

                        except:
                            pass
                    # raw_tracker.ip = None

                tracker.save()
            raw_tracker.processed = True
            raw_tracker.save()

        t1 = time.time()
        logger.info('Processed {} logs in {}ms'.format(raw_trackers.count(), (t1-t0)*1000))
