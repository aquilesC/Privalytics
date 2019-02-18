"""
    .. warning:: This file is work in progress and doesn't work as it is.
"""
import getpass
from fabric import Connection, Config

project_name = 'privalytics_test'

sudo_pass = getpass.getpass("What's your sudo remote password? ")

config = Config(overrides={'sudo': {'password': sudo_pass}})

c = Connection('digital', config=config)

# c.sudo('groupadd --system webapps')
# c.sudo(f'useradd --system --gid webapps --shell /bin/bash --home /webapps/{project_name} {project_name}')
c.sudo('apt install python3-virtualenv')
c.sudo(f'mkdir -p /webapps/{project_name}')
c.sudo(f'virtualenv /webapps/{project_name}/venv --python=/usr/bin/python3')
c.sudo(f'source /webapps/{project_name}/venv/bin/activate')
c.sudo('pip install django')

# c.run('source venv/bin/activate')
# c.run('cd Privalytics/website')
# c.run('git pull')
# c.run('./manage.py collectstatic --settings=privalytics.production_settings --noinput')
# c.run('./manage.py migrate --settings=privalytics.production_settings')
# c.run('logout')
# c.run('sudo supervisorctl reload Privalytics', pty=True)
