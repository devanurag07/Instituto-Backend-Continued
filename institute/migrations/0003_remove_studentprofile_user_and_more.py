# Generated by Django 4.1 on 2023-01-11 19:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('institute', '0002_instituteconfiguration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='HistoricalStudentProfile',
        ),
        migrations.DeleteModel(
            name='StudentProfile',
        ),
    ]
