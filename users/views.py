from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from inscripcion.models import Inscripcion


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

def login_users(request):
    if request.method == 'POST':
        numero_cuenta = request.POST['numero_cuenta']
        password = request.POST['password']
        user = authenticate(request, username=numero_cuenta, password=password)

        if user is not None:
            login(request, user)

            try:
                # Intentar obtener la instancia de Inscripcion del usuario
                inscripcion = user.alumno
            except ObjectDoesNotExist:
                # Si no existe la instancia de Inscripcion, crearla
                inscripcion = Inscripcion(numero_cuenta=user)
                inscripcion.save()

            # Verificar si el usuario es administrativo
            if user.groups.filter(name='Administrativos').exists():
                return redirect('usuarios_inscritos_grupo')

            return redirect('index')
        else:
            messages.error(request, 'Número de Cuenta o contraseña inválidos')

    return render(request, 'authenticate/login_view.html', {'messages': messages.get_messages(request)})


def logout_users(request):
    logout(request)
    # Lógica adicional después del cierre de sesión
    return redirect('login')


def es_administrador(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(es_administrador)
def vista_administrador(request):
    # Código de la vista para el administrador aquí
    return render(request, 'authenticate/inscripcion.html', {'messages': messages.get_messages(request)})
    
