# Generated by Django 3.2.8 on 2023-06-30 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscripcion', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asignatura',
            name='alumnos',
        ),
        migrations.AddField(
            model_name='asignatura',
            name='creditos',
            field=models.PositiveIntegerField(default=None),
        ),
    ]
