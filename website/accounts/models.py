from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """ Class to extend the user model. It will be useful at some point.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    email_validated = models.BooleanField(default=False)
    email_validated_date = models.DateTimeField(auto_now_add=False, null=True)

    def __str__(self):
        return "Profile(email={})".format(self.user.email)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()