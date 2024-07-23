from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User

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
            return queryset.filter(semestre_actual=self.value())

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'numero_cuenta', 'semestre_actual')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'numero_cuenta', 'password1', 'password2', 'semestre_actual'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'numero_cuenta', 'semestre_actual', 'is_staff')
    list_filter = (SemestreFilter,)  # Agregamos el filtro por semestre aquí
    search_fields = ('email', 'first_name', 'last_name', 'numero_cuenta')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', SemestreFilter)  # Agregamos el filtro por semestre aquí
    ordering = ('username',)

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Si es un formulario de creación, no se muestra el campo de usuario
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    # Resto de tus personalizaciones para el administrador

admin.site.register(User, CustomUserAdmin)
