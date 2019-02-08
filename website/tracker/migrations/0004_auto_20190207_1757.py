# Generated by Django 2.1.5 on 2019-02-07 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0003_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracker',
            name='website',
            field=models.ForeignKey(default='pythonforthelab.com', null=True, on_delete=django.db.models.deletion.SET_NULL, to='tracker.Website', to_field='website_url'),
        ),
        migrations.AlterField(
            model_name='website',
            name='website_url',
            field=models.URLField(unique=True),
        ),
    ]
