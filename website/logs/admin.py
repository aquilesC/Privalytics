from django.contrib import admin

from logs.models import TimeToStore, AccountTypeSelected

admin.site.register((TimeToStore,
                     AccountTypeSelected))
