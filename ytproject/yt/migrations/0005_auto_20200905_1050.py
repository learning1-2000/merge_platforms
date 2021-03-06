# Generated by Django 3.0.5 on 2020-09-05 02:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yt', '0004_auto_20200820_1039'),
    ]

    operations = [
        migrations.CreateModel(
            name='YoutubeCrawlTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(choices=[(1, '采集Youtube视频评论'), (2, '采集Youtube账号信息'), (3, '通过关键词采集Youtube视频'), (4, '通过关键词采集Youtube视频及评论')], default=1)),
                ('target', models.TextField(blank=True, null=True, verbose_name='任务内容')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='任务来源用户')),
            ],
        ),
        migrations.DeleteModel(
            name='YoutubeTask',
        ),
    ]
