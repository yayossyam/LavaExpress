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
        cur.execute('SELECT u.CORREO, l.PASS, r.NOMROL, r.IDROL, u.IDUSER FROM USUARIO u, LOGIN l, ROLES r WHERE u.IDUSER = l.IDUSER and u.IDROL = r.IDROL  and u.CORREO = %s',(_correo,))

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
                    return render_template('admin.html') #Manda a ruta Admin si se cumple los requisitos
                else: #Rol cliente
                    flash("Acceso denegado: solo administradores", "danger")
                    return redirect(url_for('index'))
            else:
                flash("Contraseña incorrecta", "warning")
                return redirect(url_for('index'))
        else:
            flash("Usuario no existe", "danger")
            return redirect(url_for('index'))
        
    return render_template('login.html')
        



#Redireccionar si el usuario busca una página no existente
def pagina_no_encontrada(error):
    return redirect(url_for('index'))

#Si estamos desde el archivo inicial (main), se ejecutará la aplicación
if __name__ == '__main__':
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True) #debug=True permite que cualquier cambio se aplique cuando el servidor esta activo