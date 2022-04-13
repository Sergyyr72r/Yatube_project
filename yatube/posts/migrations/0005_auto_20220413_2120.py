# Generated by Django 2.2.19 on 2022-04-13 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220412_2156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(max_length=400),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
