from django.db import models
from users.models import User

class Asignatura(models.Model):
    clave_asignatura = models.SmallIntegerField(primary_key=True)
    denominacion = models.CharField(max_length=80)
    semestre = models.PositiveIntegerField()
    creditos = models.PositiveIntegerField(default=None)
  
    
    def __str__(self):
        return self.denominacion
    


class Grupo(models.Model):
    clave_grupo = models.SmallIntegerField(primary_key= True)
    descripcion = models.CharField(max_length=100)
    asignaturas = models.ManyToManyField(Asignatura)

    def __str__(self):
        return str(self.clave_grupo)
    



class Inscripcion(models.Model):
    id = models.AutoField
    numero_cuenta = models.OneToOneField(User, on_delete=models.CASCADE)
    asignatura =models.ManyToManyField(Asignatura,blank=False)
     

    def __str__(self):
        numero_de_cuenta = "{0}"
        return numero_de_cuenta.format(self.numero_cuenta)



    

    
    
    

    
   
    

