# Generated by Django 4.2.4 on 2023-11-30 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0008_alter_cost_record_cost_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='memo',
            field=models.CharField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='user_pk_id',
            field=models.CharField(max_length=32, null=True),
        ),
    ]