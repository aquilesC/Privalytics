from django.contrib.auth.models import User
from django.core.management import BaseCommand

from accounts.models import Profile


class Command(BaseCommand):
    help = """Creates profiles for users who don't have one yet.
    """

    def handle(self, *args, **options):
        users = User.objects.all()
        user_without_profile = []
        for user in users:
            if not Profile.objects.filter(user=user).count():
                Profile.objects.create(user=user)
                user_without_profile.append(user)

        return "Done creating {} profiles".format(len(user_without_profile))