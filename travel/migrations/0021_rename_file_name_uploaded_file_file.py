# Generated by Django 4.2.4 on 2023-12-09 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0020_rename_file_uploaded_file_file_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uploaded_file',
            old_name='file_name',
            new_name='file',
        ),
    ]