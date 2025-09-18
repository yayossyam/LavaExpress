#CONFIGURACIÓN DE LA BD Y SECRET KEY PARA EL LOGIN

#Configuración de la Base de Datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',   # root sin contraseña
    'db': 'lavaexpress',
    'cursorclass': 'DictCursor'
}


# Clave secreta para sesiones
SECRET_KEY = 'clave_2020'