# Generated by Django 4.2.4 on 2023-11-25 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0003_remove_cost_record_schedule_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cost_record',
            name='schedule_pk_id',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
