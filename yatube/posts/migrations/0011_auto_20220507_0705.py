# Generated by Django 2.2.6 on 2022-05-07 07:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20220507_0649'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='group1',
            new_name='group',
        ),
    ]