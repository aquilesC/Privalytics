from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """ Class to extend the user model. It will be useful at some point.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "Profile(email={})".format(self.user.email)