# Generated by Django 5.2 on 2024-11-19 03:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('human_resource', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField(db_index=True)),
                ('end_datetime', models.DateTimeField(db_index=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('creator', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='human_resource.employee')),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentInvitee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_invitees', to='appointment.appointment')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_invitations', to='human_resource.employee')),
            ],
            options={
                'unique_together': {('appointment', 'employee')},
            },
        ),
        migrations.AddField(
            model_name='appointment',
            name='invitees',
            field=models.ManyToManyField(related_name='appointments', through='appointment.AppointmentInvitee', to='human_resource.employee'),
        ),
    ]
