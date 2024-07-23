
from django.contrib import admin
from users.models import User  # Asegúrate de importar el modelo User de la aplicación 'users'
from django.contrib import admin
from inscripcion.models import Inscripcion, Grupo, Asignatura



class SemestreFilter(admin.SimpleListFilter):
    title = 'Semestre'
    parameter_name = 'semestre_actual'

    def lookups(self, request, model_admin):
        # Obtener todos los semestres disponibles en la base de datos
        semestres = User.objects.values_list('semestre_actual', flat=True).distinct()
        choices = [(semestre, f'Semestre {semestre}') for semestre in semestres]
        return choices

    def queryset(self, request, queryset):
        if self.value():
            # Obtener los usuarios con el semestre seleccionado
            usuarios_con_semestre = User.objects.filter(semestre_actual=self.value())

            # Filtrar las inscripciones correspondientes a los usuarios con el semestre seleccionado
            inscripciones_filtradas = queryset.filter(numero_cuenta__in=usuarios_con_semestre)
            return inscripciones_filtradas

class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_asignaturas')

    def get_asignaturas(self, obj):
        return ", ".join([asignatura.denominacion for asignatura in obj.asignatura.all()])

    get_asignaturas.short_description = 'Asignaturas'

    list_filter = (SemestreFilter,)  # Agregamos el filtro por semestre aquí

    actions = ['inscribir_usuarios']

    def inscribir_usuarios(self, request, queryset):
        # Obtener las asignaturas cuyo semestre sea 3
        asignaturas_a_inscribir = Asignatura.objects.filter(semestre=3)

        # Crear la inscripción para cada usuario seleccionado y asignar las asignaturas
        for usuario in queryset:
            inscripcion, created = Inscripcion.objects.get_or_create(numero_cuenta=usuario)
            inscripcion.asignatura.set(asignaturas_a_inscribir)

        self.message_user(request, f"Se ha realizado la inscripción para {queryset.count()} usuarios.")

    inscribir_usuarios.short_description = "Inscribir usuarios seleccionados"


admin.site.register(Inscripcion, InscripcionAdmin)

admin.site.register(Asignatura)
admin.site.register(Grupo)



