# Generated by Django 4.0.5 on 2022-06-20 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0019_auto_20220618_0612'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='views',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]