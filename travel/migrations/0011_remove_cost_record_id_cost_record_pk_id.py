# Generated by Django 4.2.4 on 2023-12-03 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0010_rename_memo_list_day_introduce_memo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cost_record',
            name='id',
        ),
        migrations.AddField(
            model_name='cost_record',
            name='pk_id',
            field=models.CharField(default=1, max_length=32, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
