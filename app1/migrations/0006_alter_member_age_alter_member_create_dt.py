# Generated by Django 4.2.4 on 2023-09-04 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0005_member_order_memo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='age',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='member',
            name='create_dt',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
