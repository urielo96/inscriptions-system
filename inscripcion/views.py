from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import User, AbstractUser
from inscripcion.models import Asignatura, Inscripcion, Grupo
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.views import View
from django.db.models import Q
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Image
from django.templatetags.static import static
from datetime import datetime
from reportlab.platypus import Spacer
from reportlab.platypus import Frame
from reportlab.platypus import BaseDocTemplate, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, PageBreak
from reportlab.platypus import Image
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse


import qrcode

from django.http import FileResponse
from django.template.loader import render_to_string
from django.utils.text import slugify


def user_authenticated(user):
    return user.is_authenticated


def is_alumno(user):
    return user.is_authenticated and user.groups.filter(name='Alumnos').exists()


@login_required
@user_passes_test(is_alumno, login_url='/users/login')
def index(request):
    # Obtener el alumno actualmente autenticado desde la sesión
    alumno = request.user
    numero_cuenta = alumno.numero_cuenta
    
    # Obtener el semestre actual del alumno
    semestre_actual = alumno.semestre_actual
    
    # Obtener las asignaturas inscritas del usuario actual
    asignaturas_inscritas = alumno.alumno.asignatura.all()
    
    # Obtener todos los cursos que pertenecen al semestre actual del alumno
    cursos_listados = Asignatura.objects.filter(
        Q(semestre=semestre_actual) | Q(semestre=0))
    
    mostrar_boton_comprobante = False

    # Comprobar si el alumno es extraordinario
    if is_extraordinario(request.user):
        # Renderizar un template diferente para los alumnos extraordinarios
        return render(request, "extraordinario.html", context={
            'cursos_listados': cursos_listados,
            'asignaturas_inscritas': asignaturas_inscritas,
            'mostrar_boton_comprobante': mostrar_boton_comprobante,
        })

    return render(request, "index.html", context={
        'cursos_listados': cursos_listados,
        'asignaturas_inscritas': asignaturas_inscritas,
        'mostrar_boton_comprobante': mostrar_boton_comprobante,
    })


def redirect_to_login_if_expired(view_func):
    decorated_view_func = user_passes_test(
        user_authenticated, login_url='/users/login')(view_func)

    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.session.get_expiry_age() <= 0:
            return redirect('/users/login')
        return decorated_view_func(request, *args, **kwargs)

    return wrapper


index = redirect_to_login_if_expired(index)




@login_required
def inscribir_asignatura(request):
    if request.method == 'POST':
        asignatura_id = request.POST.get('asignatura_id')

        # Obtener el usuario actualmente autenticado
        usuario = request.user

        # Obtener la asignatura a partir del ID
        asignatura = Asignatura.objects.get(clave_asignatura=asignatura_id)

        # Obtener la instancia de Inscripcion del usuario
        inscripcion = usuario.alumno

        # Agregar la asignatura a la relación muchos a muchos utilizando el método set()
        inscripcion.asignatura.add(asignatura)

        return redirect('index')




@login_required
def eliminar_asignatura(request, asignatura_id):
    if request.method == 'POST':
        # Obtener el usuario actualmente autenticado
        usuario = request.user

        # Obtener la instancia de Inscripcion del usuario
        inscripcion = get_object_or_404(Inscripcion, numero_cuenta=usuario)

        # Obtener la asignatura a partir de la clave_asignatura
        asignatura = get_object_or_404(
            Asignatura, clave_asignatura=asignatura_id)

        # Verificar si la asignatura está en la relación muchos a muchos
        if asignatura in inscripcion.asignatura.all():
            # Eliminar la asignatura de la relación muchos a muchos utilizando el método remove()
            inscripcion.asignatura.remove(asignatura)

    return redirect('index')



def is_administrativo(user):
    return user.is_authenticated and user.groups.filter(name='Administrativos').exists() 

def is_extraordinario(user):
    return user.is_authenticated and user.groups.filter(name='Extraordinarios').exists()

@login_required
@user_passes_test(is_administrativo, login_url='/inscripcion/grupos')
def usuarios_inscritos_grupo(request):
    grupos = Grupo.objects.all()
    grupo_seleccionado = None
    usuarios_inscritos = []

    grupo_clave_str = request.GET.get('grupo', '')  # Obtener el valor del parámetro 'grupo' con un valor predeterminado de ''
    if grupo_clave_str:
        try:
            grupo_clave = int(grupo_clave_str)
            grupo_seleccionado = Grupo.objects.get(clave_grupo=grupo_clave)
            asignaturas_grupo = grupo_seleccionado.asignaturas.all()
            usuarios_inscritos = User.objects.filter(alumno__asignatura__in=asignaturas_grupo).distinct()
        except (ValueError, Grupo.DoesNotExist):
            grupo_seleccionado = None  # Manejar el caso en que el grupo no existe o el valor no es un entero válido

    context = {
        'grupos': grupos,
        'grupo_seleccionado': grupo_seleccionado,
        'usuarios': usuarios_inscritos
    }

    return render(request, 'usuarios_inscritos_grupo.html', context)




@login_required
def generar_archivo_txt(request, grupo_clave):
    grupo_seleccionado = Grupo.objects.get(clave_grupo=grupo_clave)
    # Obtenemos la clave de la asignatura de los parámetros de la URL
    clave_asignatura = request.GET.get('asignatura')
    asignatura_especifica = grupo_seleccionado.asignaturas.get(
        clave_asignatura=clave_asignatura)
    usuarios_inscritos = User.objects.filter(
        alumno__asignatura=asignatura_especifica).distinct()

    contenido = ""

    for usuario in usuarios_inscritos:
        # Aseguramos que la clave de la asignatura tenga siempre 4 dígitos con ceros a la izquierda
        clave_asignatura_padded = str(asignatura_especifica.clave_asignatura).zfill(4)
        clave_grupo_padded = str(grupo_seleccionado.clave_grupo).zfill(4)
        linea = f"{usuario.numero_cuenta}2253{clave_asignatura_padded}{clave_grupo_padded}A\n"
        contenido += linea

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="alumnos_grupo.txt"'
    response.write(contenido)

    return response



from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from django.conf import settings
from reportlab.lib import utils
import os
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.platypus import Image
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Asignatura

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Asignatura
from reportlab.lib.pagesizes import A2

@login_required
def generar_comprobante(request, alumno_id):
    try:
        alumno_info = User.objects.get(numero_cuenta=alumno_id)
    except User.DoesNotExist:
        return HttpResponse("Alumno no encontrado", status=404)
    

    asignaturas_inscritas = Asignatura.objects.filter(inscripcion__numero_cuenta=alumno_info)

    


    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize= letter)
    elements = []

    # Obtener la ruta local de la imagen a la izquierda
    image_path_left = os.path.join(settings.BASE_DIR, 'static', 'img', 'logolcf.png')

    # Cargar la imagen a la izquierda
    logo_left = Image(image_path_left, width=50, height=70)
    logo_left.hAlign = 'LEFT'  # Alineamos la imagen a la izquierda

   

    image_path_right = os.path.join(settings.BASE_DIR, 'static', 'img', 'unam_logo_azul.png')

    # Cargar la imagen a la derecha
    logo_right = Image(image_path_right, width=60, height=70)
    logo_right.hAlign = 'RIGHT'  # Alineamos la imagen a la derecha

    

    # Agregar párrafos de texto en el encabezado del PDF
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=getSampleStyleSheet()['Title'],
        fontName='Helvetica-Bold',
        alignment=1,  # 0=Left, 1=Center, 2=Right
        fontSize=10
    )
    title_styles = ParagraphStyle(
        'TitleStyles',
        parent=getSampleStyleSheet()['Title'],
        fontName='Helvetica-Bold',
        alignment=1,  # 0=Left, 1=Center, 2=Right
        fontSize=11
    )
    datas = [
        [
            logo_left,  # Logotipo izquierdo
            Paragraph("UNIVERSIDAD NACIONAL AUTONOMA DE MEXICO<br/>ESCUELA NACIONAL DE CIENCIAS FORENSES<br/>SECRETARIA DE SERVICIOS ESCOLARES", title_styles),
            logo_right,  # Logotipo derecho

        ]
    ]
    table = Table(datas, colWidths=[60, 300, 60])
    
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))
    elements.append(table)

    # Agregar título "Comprobante de Inscripción"
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))
    
    title = Paragraph("Comprobante de Inscripción", title_style)
    elements.append(title)

    # Crear una tabla para mostrar los elementos en la misma línea
    styles = getSampleStyleSheet()
    data = [
    [
        Paragraph("<b>Nombre del alumno:</b>", styles['Normal']),
        Paragraph(f"{alumno_info.first_name} {alumno_info.last_name}", styles['Normal']),
    ],
    [
        Paragraph("<b>Número de cuenta:</b>", styles['Normal']),
        Paragraph(f"{alumno_info.numero_cuenta}", styles['Normal']),
    ],
    [
        Paragraph("<b>Plan:</b>", styles['Normal']),
        Paragraph("2253", styles['Normal']),  # Aquí puedes poner el valor del plan si es dinámico
    ],
    [
        Paragraph("<b>Periodo:</b>", styles['Normal']),
        Paragraph("2024-2", styles['Normal']),  # Aquí puedes poner el valor del periodo si es dinámico
    ],
    [
        Paragraph("<b>Semestre:</b>", styles['Normal']),
        Paragraph(f"{alumno_info.semestre_actual}", styles['Normal']),  # Aquí puedes poner el valor del periodo si es dinámico
    ],
]
    table = Table(data, colWidths=[210,210])
    
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
    ]))

    
    elements.append(table)
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))

    data = [["Clave", "Nombre", "Creditos"]]
    for asignatura in asignaturas_inscritas:
        data.append([str(asignatura.clave_asignatura).zfill(4), asignatura.denominacion, asignatura.creditos])

    table = Table(data, colWidths=[60,300,60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
    
    # Asignar el ancho calculado a la tabla
    
    elements.append(table)

    
      # Obtener la fecha y hora actual
    now = datetime.now()
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

    
    # Crear el estilo para el párrafo de la fecha y hora
    date_style = ParagraphStyle(
    'DateStyle',
    parent=getSampleStyleSheet()['Normal'],
    fontName='Helvetica',
    leftIndent=20  # Agregamos el margen izquierdo de 20 puntos
)

    # Agregar la fecha y hora al PDF
    date_paragraph = Paragraph(f"<b>Fecha y hora de consulta:</b> {formatted_date}", date_style)
    date_paragraph.leftIndent = 100
    elements.append(date_paragraph)

     # Generar codigo QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=2,
    )
    data = ""  # Redirigir a pagina con informacion del alumno     
    
    qr.add_data(data)
    qr.make(fit=True)

    # Convertir el código QR en una imagen y guardarla en un objeto BytesIO
    img = qr.make_image(fill='black', back_color='white')
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')

    # Crear un objeto Image de ReportLab con la imagen del código QR
    qr_image = Image(img_buffer, width=100, height=100)  # Ajusta el tamaño según sea necesario

    # Agregar la imagen del código QR a los elementos del PDF
    elements.append(qr_image)

    




    doc.build(elements)

   
  
    # Obtener el contenido del PDF generado
    pdf_content = buffer.getvalue()
    buffer.close()

    # Devolver el contenido del PDF en la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Comprobante-{alumno_info.numero_cuenta}.pdf"'
    response.write(pdf_content)
    return response







# AQUI EMPIEZA EL CODIGO PARA GENERAR EL PDF DE LOS ALUMNOS EXTRAORDINARIOS
#####################################################################################################




@login_required
def generar_comprobante_extraordinario(request, alumno_id):
    try:
        alumno_info = User.objects.get(numero_cuenta=alumno_id)
    except User.DoesNotExist:
        return HttpResponse("Alumno no encontrado", status=404)
    


    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize= letter) 
    elements = [] 

    # Obtener la ruta local de la imagen a la izquierda
    image_path_left = os.path.join(settings.BASE_DIR, 'static', 'img', 'logolcf.png')

    # Cargar la imagen a la izquierda
    logo_left = Image(image_path_left, width=45, height=70)
    logo_left.hAlign = 'LEFT'  # Alineamos la imagen a la izquierda
    image_path_right = os.path.join(settings.BASE_DIR, 'static', 'img', 'unam_logo_azul.png')

    # Cargar la imagen a la derecha
    logo_right = Image(image_path_right, width=55, height=70)
    logo_right.hAlign = 'RIGHT'  # Alineamos la imagen a la derecha
   



    

    # Agregar párrafos de texto en el encabezado del PDF
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=getSampleStyleSheet()['Title'],
        fontName='Helvetica-Bold',
        alignment=1,  # 0=Left, 1=Center, 2=Right
        fontSize=10
    )
    title_styles = ParagraphStyle(
        'TitleStyles',
        parent=getSampleStyleSheet()['Title'],
        fontName='Helvetica-Bold',
        alignment=1,  # 0=Left, 1=Center, 2=Right
        fontSize=11
    )
    datas = [
        [
            logo_left,  # Logotipo izquierdo
            Paragraph("UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO<br/>ESCUELA NACIONAL DE CIENCIAS FORENSES<br/>SECRETARIA DE SERVICIOS ESCOLARES", title_styles),
            logo_right,  # Logotipo derecho

        ]
    ]
    
    table = Table(datas, colWidths=[60, 300, 60])
    
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))
    elements.append(table)

    elements.append(Spacer(0, 50))
    
    # Agregar título "Comprobante de Inscripción"
    
    title = Paragraph("Comprobante de Inscripción", title_style)
    
    elements.append(title)

    # Fechas de Exámen
    numeros_cuenta_misma_fecha = ['321197580', '319711813', '320013870', '319053243', '319296075']
    
    numeros_cuenta_nociones = ['321197580', '319711813']


    #Horarios de Exámen
    horarios_de_10 = ['320013870', '319053243', '319296075']

  


    # Crear una tabla para mostrar los elementos en la misma línea
    styles = getSampleStyleSheet()
    data = [
    [
        Paragraph("<b>Nombre del alumno:</b>", styles['Normal']),
        Paragraph(f"{alumno_info.first_name} {alumno_info.last_name}", styles['Normal']),
        
    ],
    [
        Paragraph("<b>Número de cuenta:</b>", styles['Normal']),
        Paragraph(f"{alumno_info.numero_cuenta}", styles['Normal']),
    ],
    [
        Paragraph("<b>Horario del Examen:</b>", styles['Normal']),
    Paragraph(
        "10:00 HORAS" if alumno_info.numero_cuenta in horarios_de_10 
        else "9:00 HORAS",
        styles['Normal']
    ),
    ],
    [
        Paragraph("<b>Fecha del Examen:</b>", styles['Normal']),
    Paragraph(
        "MARTES 16 DE ENERO DE 2024" 
        if alumno_info.numero_cuenta in numeros_cuenta_misma_fecha 
        else "MIÉRCOLES 17 DE ENERO DE 2024",
        styles['Normal']
    ),

   ],
    [
    Paragraph("<b> Asignatura:</b>", styles['Normal']),
    Paragraph(
        "NOCIONES DE DERECHO" if alumno_info.numero_cuenta in numeros_cuenta_nociones else
        "QUÍMICA FORENSE" if alumno_info.numero_cuenta == '320290509' else
        "ESTUD.DOGMAT.DELITOS ANALIS.CASOS",
        styles['Normal']
    ),
    
],
[
    
    
    Paragraph("", styles['Normal']),
    
    
    ],
    [
    
    
    Paragraph("<b>Nota:</b>Revisa que tus datos esten correctos.", styles['Normal']),
    
    
    ]
    
    
]
    table = Table(data, colWidths=[210,210])
    
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
    ]))

    
    elements.append(table)

    #Agregar QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=2,
    )
    data = "    " #necesito redirigir a la pagina de informacion del alumno
    qr.add_data(data)
    qr.make(fit=True)

    # Convertir el código QR en una imagen y guardarla en un objeto BytesIO
    img = qr.make_image(fill='black', back_color='white')
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')

    # Crear un objeto Image de ReportLab con la imagen del código QR
    qr_image = Image(img_buffer, width=100, height=100)
    qr_image.hAlign = 'RIGTH'
    elements.append(qr_image)
    elements.append(Spacer(0, 20))
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))


        
   
    
    



    

    # Construir el documento
    doc.build(elements)
   
  
    # Obtener el contenido del PDF generado
    pdf_content = buffer.getvalue()
    buffer.close()

    # Devolver el contenido del PDF en la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Comprobante-{alumno_info.numero_cuenta}.pdf"'
    response.write(pdf_content)
    return response

