# Generated by Django 2.1.5 on 2019-02-19 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('max_websites', models.IntegerField(default=0)),
                ('max_visits', models.IntegerField(default=0)),
            ],
        ),
    ]