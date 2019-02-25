from django.db import models


class AccountTypeSelected(models.Model):
    BASIC = 1
    ADVANCED = 2
    OTHER = 3
    ACCOUNT_TYPE = (
        (BASIC, 'basic'),
        (ADVANCED, 'advanced'),
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    account_type = models.IntegerField(choices=ACCOUNT_TYPE, null=True, blank=True)

    def __str__(self):
        return "Account {}".format(self.account_type)


class TimeToStore(models.Model):
    """Measures the time it takes for the view to store a tracker event.
    """
    POST_TRACK = 1
    MAKE_DASHBOARD = 2
    MAKE_WEBSITE_STATS = 3
    POST_RAW_TRACK = 4
    MEASURED = (
        (POST_TRACK, 'post_time'),
        (MAKE_DASHBOARD, 'make_dashboard'),
        (MAKE_WEBSITE_STATS, 'make_website_stats'),
        (POST_RAW_TRACK, 'post_raw_time')
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    measured_time = models.FloatField()
    measured_type = models.IntegerField(choices=MEASURED, default=POST_TRACK)

    def __str__(self):
        return "{} - Time: {:2.3f}ms".format(self.measured_type, 1000*self.measured_time)
