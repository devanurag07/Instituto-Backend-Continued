# Generated by Django 4.1 on 2023-01-11 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0002_alter_batch_blacklist_students_alter_batch_students'),
    ]

    operations = [
        migrations.RenameField(
            model_name='batch',
            old_name='batch_subject',
            new_name='subject',
        ),
        migrations.RenameField(
            model_name='historicalbatch',
            old_name='batch_subject',
            new_name='subject',
        ),
    ]
