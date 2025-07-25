# Generated by Django 5.2.3 on 2025-07-09 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_dailyrotationplan_rotationperiod'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShiftSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Nom du planning de poste (ex: 'Planning Été 2024')", max_length=200, unique=True)),
                ('type', models.CharField(choices=[('day', 'Jour'), ('shift', 'Poste')], default='day', help_text='Type de planning: jour ou poste', max_length=10)),
                ('break_times', models.PositiveIntegerField(default=2, help_text='Nombre de pauses par défaut (généralement 2)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Planning de Poste',
                'verbose_name_plural': 'Plannings de Poste',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ShiftSchedulePeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(help_text='Date de début de la période')),
                ('end_date', models.DateField(help_text='Date de fin de la période')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('shift_schedule', models.ForeignKey(help_text='Planning de poste auquel appartient cette période', on_delete=django.db.models.deletion.CASCADE, related_name='periods', to='core.shiftschedule')),
            ],
            options={
                'verbose_name': 'Période de Planning de Poste',
                'verbose_name_plural': 'Périodes de Planning de Poste',
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='ShiftScheduleWeek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_number', models.PositiveIntegerField(help_text='Numéro de la semaine dans la période (1, 2, 3, etc.)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('period', models.ForeignKey(help_text='Période à laquelle appartient cette semaine', on_delete=django.db.models.deletion.CASCADE, related_name='weeks', to='core.shiftscheduleperiod')),
            ],
            options={
                'verbose_name': 'Semaine de Planning',
                'verbose_name_plural': 'Semaines de Planning',
                'ordering': ['period', 'week_number'],
                'unique_together': {('period', 'week_number')},
            },
        ),
        migrations.CreateModel(
            name='ShiftScheduleDailyPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.IntegerField(choices=[(1, 'Lundi'), (2, 'Mardi'), (3, 'Mercredi'), (4, 'Jeudi'), (5, 'Vendredi'), (6, 'Samedi'), (7, 'Dimanche')], help_text='Jour de la semaine (1=Lundi, 7=Dimanche)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('daily_rotation_plan', models.ForeignKey(help_text='Rythme quotidien assigné à ce jour', on_delete=django.db.models.deletion.PROTECT, to='core.dailyrotationplan')),
                ('week', models.ForeignKey(help_text='Semaine à laquelle appartient ce plan quotidien', on_delete=django.db.models.deletion.CASCADE, related_name='daily_plans', to='core.shiftscheduleweek')),
            ],
            options={
                'verbose_name': 'Plan Quotidien de Planning',
                'verbose_name_plural': 'Plans Quotidiens de Planning',
                'ordering': ['week', 'weekday'],
                'unique_together': {('week', 'weekday')},
            },
        ),
    ]
