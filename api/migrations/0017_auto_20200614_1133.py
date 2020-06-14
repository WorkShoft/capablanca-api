# Generated by Django 3.0.5 on 2020-06-14 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20200614_1012'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='start_timestamp',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='end_timestamp',
            new_name='finished_at',
        ),
        migrations.AddField(
            model_name='game',
            name='started_at',
            field=models.DateTimeField(null=True),
        ),
    ]