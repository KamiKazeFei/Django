# Generated by Django 4.2.4 on 2023-11-25 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0005_alter_cost_record_schedule_pk_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='day_introduce',
            name='ser_no',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
