# Generated by Django 4.2.4 on 2023-12-09 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0016_uploaded_file_cost_record_ser_no_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cost_record',
            name='ser_no',
            field=models.IntegerField(default=0, max_length=6),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='schedule',
            name='real_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, null=True),
        ),
    ]