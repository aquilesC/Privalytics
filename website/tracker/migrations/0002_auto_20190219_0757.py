# Generated by Django 2.1.5 on 2019-02-19 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracker',
            name='website',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trackers', to='tracker.Website', to_field='website_url'),
        ),
    ]