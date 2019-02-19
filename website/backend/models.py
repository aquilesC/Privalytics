from django.db import models


class Message(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user_email = models.EmailField(blank=False)
    message = models.TextField(blank=False)

    def __str__(self):
        return "Message from {}".format(self.user_email)


class AccountTypes(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    max_websites = models.IntegerField(default=0, null=False, blank=False)
    max_visits = models.IntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return "Account Type {}".format(self.name)
