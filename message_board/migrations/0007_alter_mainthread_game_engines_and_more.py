# Generated by Django 4.2.8 on 2023-12-28 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message_board', '0006_alter_mainthread_game_engines_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainthread',
            name='game_engines',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mainthread',
            name='genres',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mainthread',
            name='involved_companies',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mainthread',
            name='platforms',
            field=models.TextField(blank=True, null=True),
        ),
    ]
