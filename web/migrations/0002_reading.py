# Generated by Django 3.2.6 on 2021-08-12 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gadgetdb', '0001_initial'),
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('rdg_no', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('temp', models.FloatField(blank=True, null=True)),
                ('rh', models.FloatField(blank=True, null=True)),
                ('pm_01', models.FloatField(blank=True, null=True)),
                ('pm_25', models.FloatField(blank=True, null=True)),
                ('pm_10', models.FloatField(blank=True, null=True)),
                ('bin_0', models.FloatField(blank=True, null=True)),
                ('bin_1', models.FloatField(blank=True, null=True)),
                ('bin_2', models.FloatField(blank=True, null=True)),
                ('bin_3', models.FloatField(blank=True, null=True)),
                ('bin_4', models.FloatField(blank=True, null=True)),
                ('bin_5', models.FloatField(blank=True, null=True)),
                ('bin_6', models.FloatField(blank=True, null=True)),
                ('bin_7', models.FloatField(blank=True, null=True)),
                ('bin_8', models.FloatField(blank=True, null=True)),
                ('bin_9', models.FloatField(blank=True, null=True)),
                ('bin_10', models.FloatField(blank=True, null=True)),
                ('bin_11', models.FloatField(blank=True, null=True)),
                ('bin_12', models.FloatField(blank=True, null=True)),
                ('bin_13', models.FloatField(blank=True, null=True)),
                ('bin_14', models.FloatField(blank=True, null=True)),
                ('bin_15', models.FloatField(blank=True, null=True)),
                ('bin_16', models.FloatField(blank=True, null=True)),
                ('bin_17', models.FloatField(blank=True, null=True)),
                ('bin_18', models.FloatField(blank=True, null=True)),
                ('bin_19', models.FloatField(blank=True, null=True)),
                ('bin_20', models.FloatField(blank=True, null=True)),
                ('bin_21', models.FloatField(blank=True, null=True)),
                ('bin_22', models.FloatField(blank=True, null=True)),
                ('bin_23', models.FloatField(blank=True, null=True)),
                ('bin1_mtof', models.FloatField(blank=True, null=True)),
                ('bin3_mtof', models.FloatField(blank=True, null=True)),
                ('bin5_mtof', models.FloatField(blank=True, null=True)),
                ('bin7_mtof', models.FloatField(blank=True, null=True)),
                ('sampling_period', models.FloatField(blank=True, null=True)),
                ('sample_flow_rate', models.FloatField(blank=True, null=True)),
                ('reject_count_glitch', models.FloatField(blank=True, null=True)),
                ('reject_count_longtof', models.FloatField(blank=True, null=True)),
                ('reject_count_ratio', models.FloatField(blank=True, null=True)),
                ('reject_count_outofrange', models.FloatField(blank=True, null=True)),
                ('fan_rev_count', models.FloatField(blank=True, null=True)),
                ('last_status', models.FloatField(blank=True, null=True)),
                ('checksum', models.FloatField(blank=True, null=True)),
                ('gadget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gadgetdb.gadget')),
            ],
        ),
    ]