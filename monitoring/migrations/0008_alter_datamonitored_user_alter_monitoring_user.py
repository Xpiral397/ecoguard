# Generated by Django 5.0.2 on 2024-02-22 08:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0007_alter_datamonitored_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datamonitored',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='monitoring.user'),
        ),
        migrations.AlterField(
            model_name='monitoring',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='monitoring.user'),
        ),
    ]
