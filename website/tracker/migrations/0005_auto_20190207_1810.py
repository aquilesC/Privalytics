# Generated by Django 2.1.5 on 2019-02-07 18:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_auto_20190207_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracker',
            name='website',
            field=models.ForeignKey(default='pythonforthelab.com', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trackers', to='tracker.Website', to_field='website_url'),
        ),
    ]