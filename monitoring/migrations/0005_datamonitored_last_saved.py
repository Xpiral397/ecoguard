# Generated by Django 5.0.2 on 2024-02-21 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0004_alter_datamonitored_end_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='datamonitored',
            name='last_saved',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
