from django.db import models


class TimeToStore(models.Model):
    """Measures the time it takes for the view to store a tracker event.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    measured_time = models.FloatField()

    def __str__(self):
        return "Time: {:2.3f}s".format(self.measured_time)