from django.urls import path
from . import views

urlpatterns = [
    # #     path('',views.login_view, name='login_view'),
    path('index/', views.index, name='index'),
    
    path('inscribr_asignatura/', views.inscribir_asignatura,
         name='inscribir_asignatura'),
    path('eliminar_asignatura/<int:asignatura_id>/',
         views.eliminar_asignatura, name='eliminar_asignatura'),
       
    path('grupos/',views.usuarios_inscritos_grupo, name='usuarios_inscritos_grupo'),
    path('generar_archivo_txt/<int:grupo_clave>/', views.generar_archivo_txt, name='generar_archivo_txt'),
    path('generar_comprobante/<str:alumno_id>/', views.generar_comprobante, name='generar_comprobante'),
    path('generar_comprobante_extraordinario/<str:alumno_id>/', views.generar_comprobante_extraordinario, name='generar_comprobante_extraordinario')
    

]
