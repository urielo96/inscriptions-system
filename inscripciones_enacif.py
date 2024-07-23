import pandas as pd

# Leer el archivo Excel
inscripcion = pd.read_excel('inscripciones_enacif.xlsx')

# Seleccionar solo las columnas deseadas, reemplaza 'columna1', 'columna2',... con los nombres reales de tus columnas
columnas_deseadas = ['No. de Cuenta', 'Nombre', 'CVE','ASIGNATURA','GRUPO']
inscripcion_filtrada = inscripcion.loc[:, columnas_deseadas]

# Imprimir las primeras filas para verificar
print(inscripcion_filtrada.head(18))