"""
    .. warning:: This file is work in progress and doesn't work as it is.
"""

import getpass
from fabric import Connection, Config


sudo_pass = getpass.getpass("What's your sudo password?")

config = Config(overrides={'sudo': {'password': sudo_pass}})

c = Connection('digital')
c.run('sudo su - privalytics', pty=True)
c.run('source venv/bin/activate')
c.run('cd Privalytics/website')
c.run('git pull')
c.run('./manage.py collectstatic --settings=privalytics.production_settings --noinput')
c.run('./manage.py migrate --settings=privalytics.production_settings')
c.run('logout')
c.run('sudo supervisorctl reload Privalytics', pty=True)
