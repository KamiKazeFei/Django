# Generated by Django 4.2.4 on 2023-12-09 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0017_cost_record_ser_no_alter_schedule_real_cost'),
    ]

    operations = [
        migrations.DeleteModel(
            name='uploaded_file',
        ),
    ]