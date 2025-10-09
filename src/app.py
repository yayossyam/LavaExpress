from flask import Flask
from flask import render_template, request, redirect, flash, url_for, Response, session
from flask_mysqldb import MySQL, MySQLdb #Instancia de la DB
from config import DB_CONFIG, SECRET_KEY
from bcrypt import checkpw

app = Flask(__name__) #Se inicializa la aplicación en la variable llamada "app" y recibirá la instancia de Flask
app.secret_key = SECRET_KEY

# Configuración de MySQL para flask_mysqldb
app.config['MYSQL_HOST'] = DB_CONFIG['host']
app.config['MYSQL_USER'] = DB_CONFIG['user']
app.config['MYSQL_PASSWORD'] = DB_CONFIG['password']
app.config['MYSQL_DB'] = DB_CONFIG['db']
app.config['MYSQL_CURSORCLASS'] = DB_CONFIG['cursorclass']
mysql= MySQL(app)

#Ruta INICIAL
@app.route('/')
def index():
    return render_template('login.html')

#Función de LOGIN
@app.route('/acceso-login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        #Capturamos los valores del correo
        _correo = request.form['username']
        #Capturamos los valores de la contraseña
        _password = request.form['password']

        #Creamos cursor y hacemos consulta
        cur=mysql.connection.cursor()

        #Este SELECT solo buscará que el correo ingresado exista en la BD
        cur.execute('SELECT u.IDUSER, r.IDROL, u.CORREO, u.PASS FROM USUARIO u, ROLES r WHERE u.CORREO = %s',(_correo,))

        #Variable de inicio de sesión
        account = cur.fetchone()

        #Cirre del cursor de la BD
        cur.close()

        #Validación de acceso
        if  account:
            #Aquí vamos a ver si la contraseña ingresada es igual a la de la BD
            if account['PASS'] == _password:
                session['logueado'] = True
                session['id'] = account['IDUSER'] 

                #Identificación de rol
                if account['IDROL'] == 1: #Rol administrativo
                    return render_template('administrador/admin.html') #Manda a ruta Admin si se cumple los requisitos
                else: #Rol cliente
                    return render_template('cliente/client.html')
            else:
                flash("Contraseña incorrecta", "warning")
                return redirect(url_for('index'))
        else:
            flash("Usuario no existe", "danger")
            return redirect(url_for('index'))
        
    return render_template('login.html')
        
#Función de Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'nombre' in request.form and 'apellido' in request.form and 'correo' in request.form and 'password' in request.form:

        #Capturamos los datos que el usuario ingreso
        nombre = request.form['nombre']
        apaterno = request.form['apellido']
        correo = request.form['correo']
        password = request.form['password']

        #Creamos cursor
        cur=mysql.connection.cursor()

        #Obtener el ultimo ID de USUARIO
        cur.execute('SELECT MAX(IDUSER) AS max_id FROM USUARIO')
        result = cur.fetchone()
        id = (result['max_id'] or 0) + 1
        

        #Este INSERT se realizará en la tabla USUARIO
        cur.execute('INSERT INTO USUARIO (IDUSER, IDROL, NOMBRE, APATERNO, CORREO, PASS) VALUES (%s,%s,%s,%s, %s, %s)', (id,2, nombre, apaterno, correo, password))


        #Se confirma el INSERT
        mysql.connection.commit()

        #Se cierra el cursor
        cur.close()

        flash("Usuario Registrado de manera exitosa","success")
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

#Funcion de Reportes
@app.route('/reporte')
def inicioreporte():
    return render_template('administrador/reportes/index.html')

#Administrador
#Función Inicio Administrador      
@app.route('/inicioAdmin')
def inicioAdmin():
    return render_template('administrador/admin.html')

#Función CRUD Materia Prima
@app.route('/materiaPrima')
def materiaPrima():
    return render_template('administrador/materiaPrima.html')

#Redireccionar si el usuario busca una página no existente
def pagina_no_encontrada(error):
    return redirect(url_for('index'))

#Si estamos desde el archivo inicial (main), se ejecutará la aplicación
if __name__ == '__main__':
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True) #debug=True permite que cualquier cambio se aplique cuando el servidor esta activo