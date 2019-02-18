"""
    .. warning:: This file is work in progress and doesn't work as it is.
"""
import getpass
from fabric import Connection, Config

project_name = 'privalytics'

sudo_pass = getpass.getpass("What's your sudo remote password? ")

config = Config(overrides={'sudo': {'password': sudo_pass}})

c = Connection('digital', config=config)
with c.cd(f'/webapps/{project_name}/Privalytics/website'):
    c.run('git pull')
    c.run('../../venv/bin/pip install -r requirements.txt')
    c.run('../../venv/bin/python manage.py migrate --settings=privalytics.production_settings --noinput')
    c.run('../../venv/bin/python manage.py collectstatic --settings=privalytics.production_settings --noinput')

c.sudo('supervisorctl restart Privalytics')
c.sudo('systemctl reload nginx')