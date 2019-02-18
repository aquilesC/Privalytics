from django.db import models


class Message(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user_email = models.EmailField(blank=False)
    message = models.TextField(blank=False)

    def __str__(self):
        return "Message from {}".format(self.user_email)
