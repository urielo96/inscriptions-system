from django.db import models
from users.models import User


class Asignatura(models.Model):
    clave_asignatura = models.SmallIntegerField(primary_key=True)
    denominacion = models.CharField(max_length=80)
    
    options = ((1,'Obligatoria'),
             (2,'Optativa'))
    
    caracter = models.PositiveSmallIntegerField(choices= options, default = 1)
    
    def get_caracter_display(self):
        return dict(self.options).get(self.caracter, '')
    opciones = (
        (0, 'Optativa'),
        (1, 'Primer Semestre'),
        (2, 'Segundo Semestre'),
        (3, 'Tercer Semestre'),
        (4, 'Cuarto Semestre'),
        (5, 'Quinto Semestre'),
        (6, 'Sexto Semestre'),
        (7, 'Séptimo Semestre'),
        (8, 'Octavo Semestre'),
        
    )
    semestre = models.PositiveSmallIntegerField(choices= opciones, default = 1)
    opciones_eje = ((1,'A'),
                    (2,'B'),
                    (3,'M'),
                    (4,'T')
                    )
    creditos = models.PositiveSmallIntegerField(default=0)
    eje = models.PositiveSmallIntegerField(choices= opciones_eje, default = 1)
  
    class Meta:
        ordering = ['semestre', 'clave_asignatura']
    def __str__(self):
        return f"{self.clave_asignatura} - {self.denominacion}"


class Grupo(models.Model):
    clave_grupo = models.SmallIntegerField(primary_key=True)
    opciones = (
        (1, 'Primer Semestre'),
        (2, 'Segundo Semestre'),
        (3, 'Tercer Semestre'),
        (4, 'Cuarto Semestre'),
        (5, 'Quinto Semestre'),
        (6, 'Sexto Semestre'),
        (7, 'Séptimo Semestre'),
        (8, 'Octavo Semestre'),
        (9, 'Noveno Semestre'),
    )
    semestre = models.PositiveSmallIntegerField(choices= opciones)
    asignaturas = models.ManyToManyField(Asignatura,related_name='asignaturas')
    
 

    def __str__(self):
        return str(self.clave_grupo)


# models.py

class Periodo(models.Model):
    codigo = models.CharField(max_length=7, unique=True)  # Ej. "2023-1", "2023-2"
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Desactivar los demás periodos
        if self.activo:
            Periodo.objects.exclude(pk=self.pk).update(activo=False)
        super(Periodo, self).save(*args, **kwargs)


    def __str__(self):
        return self.codigo

class Inscripcion(models.Model):
    id = models.AutoField(primary_key=True)
    numero_cuenta = models.OneToOneField(User,on_delete=models.CASCADE, related_name='alumno')
    asignatura = models.ManyToManyField(Asignatura, blank=False)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, default=1)  # Asigna el id de un periodo existente
    grupo = models.ManyToManyField(Grupo, related_name='inscripciones')  # Mantener ManyToManyField
    


    class Meta:
        verbose_name = 'Inscripcion'
        verbose_name_plural = 'Inscripciones'
        unique_together = ('numero_cuenta', 'periodo')
      

    def __str__(self):
        return str(self.numero_cuenta)
        


