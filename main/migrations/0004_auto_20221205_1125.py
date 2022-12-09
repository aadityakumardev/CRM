# Generated by Django 3.2.4 on 2022-12-05 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20221204_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='closedlog',
            name='is_close',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='closedlog',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='closedlog',
            name='logId',
            field=models.CharField(default='', max_length=50, primary_key=True, serialize=False),
        ),
    ]