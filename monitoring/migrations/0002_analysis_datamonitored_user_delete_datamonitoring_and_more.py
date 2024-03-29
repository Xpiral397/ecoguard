# Generated by Django 5.0.2 on 2024-02-21 07:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NDVI', models.DecimalField(decimal_places=2, max_digits=10)),
                ('NDWI', models.DecimalField(decimal_places=2, max_digits=10)),
                ('SDVI', models.DecimalField(decimal_places=2, max_digits=10)),
                ('NDBI', models.DecimalField(decimal_places=2, max_digits=10)),
                ('SAVI', models.DecimalField(decimal_places=2, max_digits=10)),
                ('MSAVI2', models.DecimalField(decimal_places=2, max_digits=10)),
                ('EVI', models.DecimalField(decimal_places=2, max_digits=10)),
                ('MNDWI', models.DecimalField(decimal_places=2, max_digits=10)),
                ('DeforestMeasure', models.DecimalField(decimal_places=2, max_digits=10)),
                ('LMI', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='DataMonitored',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('coordinate', models.JSONField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('last_check', models.DateTimeField(auto_now_add=True)),
                ('analysis_made', models.JSONField()),
                ('state', models.CharField(choices=[('Processing', 'Processing'), ('Error', 'Error'), ('Success', 'Success')], default='Processing', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='DataMonitoring',
        ),
        migrations.AddField(
            model_name='analysis',
            name='data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='monitoring.datamonitored'),
        ),
        migrations.AddField(
            model_name='analysis',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='monitoring.user'),
        ),
        migrations.CreateModel(
            name='Monitoring',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='monitoring.user')),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='monitoring.analysis')),
            ],
        ),
    ]
