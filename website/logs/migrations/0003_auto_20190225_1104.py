# Generated by Django 2.1.5 on 2019-02-25 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0002_auto_20190218_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetostore',
            name='measured_type',
            field=models.IntegerField(choices=[(1, 'post_time'), (2, 'make_dashboard'), (3, 'make_website_stats'), (4, 'post_raw_time')], default=1),
        ),
    ]
