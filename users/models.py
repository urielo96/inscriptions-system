from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    numero_cuenta = models.CharField(max_length=9, unique=True, null=False)
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
    semestre_actual = models.IntegerField(choices=opciones)
    USERNAME_FIELD = 'numero_cuenta'
    REQUIRED_FIELDS = ['username','password']

    

    def __str__(self):
        return f'{self.first_name},{self.numero_cuenta}'