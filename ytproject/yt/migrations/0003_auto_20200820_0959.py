# Generated by Django 3.0.5 on 2020-08-20 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yt', '0002_auto_20200820_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtubeaccount',
            name='info',
            field=models.TextField(blank=True, default='', verbose_name='频道信息'),
        ),
        migrations.AddField(
            model_name='youtubeaccount',
            name='related_channels',
            field=models.TextField(blank=True, default='', verbose_name='相关频道'),
        ),
        migrations.AlterField(
            model_name='youtubeaccount',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='博主频道描述'),
        ),
    ]
