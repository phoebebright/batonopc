# Generated by Django 3.2.6 on 2021-08-12 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gadget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref', models.UUIDField(editable=False)),
                ('factory_id', models.CharField(help_text='BT ID', max_length=100, unique=True)),
                ('status', models.CharField(choices=[('_', 'Out of Service'), ('A', 'Active'), ('R', 'Redundent'), ('T', 'Test Mode'), ('S', 'Spare'), ('U', 'Unknown')], default='_', max_length=1)),
                ('last_received_data', models.DateTimeField(blank=True, help_text='Automatically updated if data received via gascloud', null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
