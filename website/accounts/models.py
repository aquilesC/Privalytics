from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Profile(models.Model):
    """ Class to extend the user model. It will be useful at some point.
    """
    BEGINNER = 0
    BLOGGER = 1
    ADVANCED = 2
    ACCOUNT_TYPES = (
        (BEGINNER, 'beginner'),
        (BLOGGER, 'blogger'),
        (ADVANCED, 'advanced')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    email_validated = models.BooleanField(default=False)
    email_validated_date = models.DateTimeField(auto_now_add=False, null=True)
    account_id = models.CharField(max_length=12, unique=True)
    account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=BEGINNER, null=False, blank=False)
    max_websites = models.IntegerField(default=0, help_text='maximum number of websites that can be registerd')
    can_geolocation = models.BooleanField(default=False, null=True)
    account_selected = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "Profile(email={})".format(self.user.email)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.account_id = "PL-" + uuid.uuid4().hex[:6].upper()
        super(Profile, self).save(*args, **kwargs)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
