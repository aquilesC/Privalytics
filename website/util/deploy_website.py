import getpass
from fabric import Connection, Config


sudo_pass = getpass.getpass("What's your sudo password?")

config = Config(overrides={'sudo': {'password': sudo_pass}})

c = Connection('digital', config=config)
c.sudo('su - privalytics', hide='stderr')
c.run('source venv/bin/activate')
c.run('cd Privalytics/website')
c.run('git pull')
c.run('./manage.py collectstatic --settings=privalytics.production_settings --noinput')
c.run('./manage.py migrate --settings=privalytics.production_settings')
c.run('logout')
c.sudo('supervisorctl reload Privalytics', hide='stderr')
