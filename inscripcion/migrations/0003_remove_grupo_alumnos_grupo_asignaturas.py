# Generated by Django 5.1.2 on 2024-11-12 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscripcion', '0002_remove_grupo_asignaturas_grupo_alumnos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grupo',
            name='alumnos',
        ),
        migrations.AddField(
            model_name='grupo',
            name='asignaturas',
            field=models.ManyToManyField(related_name='asignaturas', to='inscripcion.asignatura'),
        ),
    ]
