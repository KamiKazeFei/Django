# Generated by Django 4.2.4 on 2023-12-19 14:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0031_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
