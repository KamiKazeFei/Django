# Generated by Django 4.2.4 on 2023-09-04 03:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='create_dt',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]