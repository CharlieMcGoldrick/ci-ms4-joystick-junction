# Generated by Django 4.2.8 on 2023-12-26 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message_board', '0003_alter_mainthread_game_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainthread',
            name='age_ratings',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainthread',
            name='aggregated_rating',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainthread',
            name='artwork',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainthread',
            name='cover',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainthread',
            name='first_release_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainthread',
            name='game_engines',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainthread',
            name='genres',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainthread',
            name='involved_companies',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainthread',
            name='platforms',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainthread',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
    ]