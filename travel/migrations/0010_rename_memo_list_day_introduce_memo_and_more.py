# Generated by Django 4.2.4 on 2023-12-03 02:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0009_alter_schedule_memo_alter_schedule_user_pk_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='day_introduce',
            old_name='memo_list',
            new_name='memo',
        ),
        migrations.RenameField(
            model_name='day_introduce',
            old_name='shopping_list',
            new_name='shopping_detail',
        ),
    ]
