from flask import Flask, send_file
from flask import render_template, request, redirect, flash, url_for, Response, session,jsonify
from flask_mysqldb import MySQL, MySQLdb #Instancia de la DB
from config import DB_CONFIG, SECRET_KEY
from bcrypt import checkpw
from datetime import date
import json
from math import ceil
#Importaciones para el PDF
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from decimal import Decimal
#Importaciones para el CORREO
from flask_mail import Mail, Message
import threading #Permite hilos que optimizan la espera de los correos
import os, base64


app = Flask(__name__) #Se inicializa la aplicación en la variable llamada "app" y recibirá la instancia de Flask
app.secret_key = SECRET_KEY

# Configuración de MySQL para flask_mysqldb
app.config['MYSQL_HOST'] = DB_CONFIG['host']
app.config['MYSQL_USER'] = DB_CONFIG['user']
app.config['MYSQL_PASSWORD'] = DB_CONFIG['password']
app.config['MYSQL_DB'] = DB_CONFIG['db']
app.config['MYSQL_CURSORCLASS'] = DB_CONFIG['cursorclass']
app.config['MYSQL_PORT'] = DB_CONFIG['port']
mysql= MySQL(app)

# Configuración para el MAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lavaexpressoficiaal@gmail.com'  #Correo Personal
app.config['MAIL_PASSWORD'] = 'vppc eqvn gkks gzvb'     #Contraseña creada para la aplicación
app.config['MAIL_DEFAULT_SENDER'] = ('LavaExpress', 'lavaexpressoficiaal@gmail.com')
mail = Mail(app)

# Metodos para el Correo
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def enviar_correo_bienvenida(correo_destino, nombre_usuario):
    asunto = "🎉 Registro exitoso en LavaExpress"

    # Contruccion de Ruta Absouluta del CSS
    css_path = os.path.join(app.root_path, 'static', 'css', 'correo.css')

    # Ruta absoluta del logo
    logo_path = os.path.join(app.root_path, 'static', 'img', 'logoLavaExpress.png')

    #Leer CSS
    try:
        with open(css_path, 'r', encoding= 'utf-8') as f:
            css_contenido = f.read()
    except FileNotFoundError:
        print(f"⚠️ No se encontró el archivo CSS en {css_path}")
        css_contenido = ""

    # Leer imagen del logo como Base64 (para mostrarla en correos locales)
    try:
        with open(logo_path, 'rb') as img_file:
            logo_b64 = base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"⚠️ No se encontró el logo en {logo_path}")
        logo_b64 = None
    
    # Renderizar el HTML
    cuerpo_html = render_template('correo_bienvenida.html', nombre_usuario = nombre_usuario, css_contenido = css_contenido, logo_b64 = logo_b64)
    
    msg = Message(asunto, recipients=[correo_destino], html= cuerpo_html)

    hilo = threading.Thread(target=send_async_email, args=(app, msg))
    hilo.start()

def enviar_correo_nuevo_pedido(correo_destino, nombre_usuario, idpedido, fecha_entrega, prendas, peso_total, costo_total):
    asunto = f"🧺 Pedido #{idpedido} registrado en LavaExpress"

    #Ruts CSS
    css_path = os.path.join(app.root_path, 'static', 'css', 'correo.css')
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_contenido = f.read()
    except FileNotFoundError:
        css_contenido = ""

    # Logo
    logo_path = os.path.join(app.root_path, 'static', 'img', 'logoLavaExpress.png')
    logo_b64 = None
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as img:
            logo_b64 = base64.b64encode(img.read()).decode('utf-8')

    # Renderizamos HTML
    cuerpo_html = render_template('correo_nuevo_pedido.html', 
                                nombre_usuario = nombre_usuario,
                                idpedido = idpedido, 
                                fecha_entrega = fecha_entrega, 
                                prendas = prendas, 
                                peso_total = peso_total, 
                                costo_total = costo_total, 
                                css_contenido = css_contenido, 
                                logo_b64 = logo_b64)
    
    msg = Message(asunto, recipients=[correo_destino], html=cuerpo_html)

    hilo = threading.Thread(target=send_async_email, args=(app, msg))
    hilo.start()

def enviar_correo_cambio_estatus(correo_destino, nombre_usuario, idpedido, fecha_entrega, estatus, prendas, peso_total, costo_total):
    # Definir asunto según el estatus
    if estatus == 'En preparación':
        asunto = f"🔧 Pedido #{idpedido} ha iniciado: {estatus}"
    elif estatus == 'Listo':
        asunto = f"✅ Pedido #{idpedido} está listo para entrega"
    else:
        asunto = f"📦 Pedido #{idpedido} actualizado"

    # CSS
    css_path = os.path.join(app.root_path, 'static', 'css', 'correo.css')
    try:
        with open(css_path, 'r', encoding= 'utf-8') as f:
            css_contenido = f.read()
    except FileNotFoundError:
        css_contenido= ""

    # Logo
    logo_path = os.path.join(app.root_path, 'static', 'img', 'logoLavaExpress.png')
    logo_b64 = None
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as img:
            logo_b64 = base64.b64encode(img.read()).decode('utf-8')

    # Renderizar HTML
    cuerpo_html = render_template(
        'correo_pedido.html',
        nombre_usuario=nombre_usuario,
        idpedido=idpedido,
        fecha_entrega=fecha_entrega,
        prendas=prendas,
        peso_total=peso_total,
        costo_total=costo_total,
        css_contenido=css_contenido,
        logo_b64=logo_b64,
        estatus=estatus
    )

    # Enviar Correo
    msg = Message(asunto, recipients=[correo_destino], html=cuerpo_html)
    hilo = threading.Thread(target=send_async_email, args=(app, msg))
    hilo.start()


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
        cur.execute("""
            SELECT IDUSER, IDROL, NOMBRE, APATERNO, CORREO, PASS
            FROM USUARIO
            WHERE CORREO = %s
        """, (_correo,))

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
                session['rol'] = account['IDROL']
                session['nombre'] = account['NOMBRE']
                session['apellido'] = account['APATERNO']

                #Identificación de rol
                if account['IDROL'] == 1: #Rol administrativo
                    return redirect(url_for('inicioAdmin')) #Manda a ruta Admin si se cumple los requisitos
                else: #Rol cliente
                    return redirect(url_for('misPedidos'))
            else:
                flash("⚠️Contraseña incorrecta", "warning")
                return redirect(url_for('index'))
        else:
            flash("❌Usuario no existe", "danger")
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

        # Enviar correo de bienvenida
        try:
            enviar_correo_bienvenida(correo, nombre)
        except Exception as e:
            print(f"❌ Error al enviar el correo: {e}")

        flash("✅Usuario Registrado de manera exitosa","success")
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

#Funcion de Reportes
@app.route('/reporte')
def inicioreporte():
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa")
        return redirect(url_for('login'))
    
    if session.get != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))
    return render_template('administrador/reportes/index.html')

#Administrador
#Crear Usuarios     
@app.route('/inicioAdmin', methods=['GET', 'POST'])
def inicioAdmin():
    
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST' and 'nombre' in request.form and 'apellido' in request.form and 'correo' in request.form and 'password' in request.form and 'rol' in request.form:
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        contra = request.form['password']
        rol = request.form['rol']

        #Creamos instancia BD
        cur = mysql.connection.cursor()

        #Verificar que solo exista un correo dado de alta
        cur.execute('SELECT * FROM USUARIO WHERE CORREO = %s', (correo,))
        existente = cur.fetchone()

        if existente:
            flash ("❌El correo ya esta en uso", "danger")
            return redirect(url_for('inicioAdmin'))
        
        #Obtenemos el ultimo ID
        cur.execute('SELECT MAX(IDUSER) AS max_id FROM USUARIO')
        resultado = cur.fetchone()
        id = (resultado['max_id'] or 0) + 1

        #Si no existe correo, procedemos a generar INSERT
        cur.execute('INSERT INTO USUARIO (IDUSER, IDROL, NOMBRE, APATERNO, CORREO, PASS) VALUES (%s, %s, %s, %s, %s, %s)', (id, rol, nombre, apellido, correo, contra))

        #Guardamos COMMIT
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        # Enviar correo de bienvenida
        try:
            enviar_correo_bienvenida(correo, nombre)
        except Exception as e:
            print(f"❌ Error al enviar correo de bienvenida: {e}")

        #Mensaje de exito
        flash("✅ Usuario registrado correctamente", "success")

        return redirect(url_for('inicioAdmin'))
    
    #Si es GET, mostramos los roles existentes
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDROL, NOMROL FROM ROLES')
    roles = cur.fetchall()
    cur.close()

    return render_template('administrador/nuevoUsuario/admin.html', roles = roles)

#Ver Usuario
@app.route('/verUsuarios', methods=['GET'])
def verUsuarios():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()

    #Necesitamos CONCATENAR USUARIO Y ROLES
    cur.execute("""SELECT u.IDUSER, CONCAT(u.NOMBRE, ' ', u.APATERNO) AS nombre_completo, r.NOMROL FROM USUARIO u JOIN ROLES r ON u.IDROL = r.IDROL """)
    usuarios = cur.fetchall()
    cur.close()
    return render_template('administrador/nuevoUsuario/verUsuarios.html', usuarios = usuarios)

#Editar Usuario
@app.route('/verUsuarios/editar_usuarios/<int:idusuario>', methods=['GET', 'POST'])
def editar_usuarios(idusuario):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST' and 'nombre' in request.form and 'apellido' in request.form and 'rol' in request.form:

        #Capturamos nuevos datos ingresados
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        rol = request.form['rol']

        #Creamos instancia BD
        cur = mysql.connection.cursor()

        #Generamos UPDATE
        cur.execute('UPDATE USUARIO SET IDROL = %s, NOMBRE = %s, APATERNO = %s WHERE IDUSER = %s', (rol, nombre, apellido, idusuario))

        #Guardamos UPDATE
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Dato actualizado correctamente", "success")

        return redirect(url_for('verUsuarios'))
    
    #Si es GET, mostramos datos a editar
    cur = mysql.connection.cursor()

    #Mostramos todos los roles existentes al usuario
    cur.execute("SELECT IDROL, NOMROL FROM ROLES")
    roles = cur.fetchall()

    #Mostramos los valores actuales del valor a editar
    cur.execute("""SELECT U.IDUSER, U.NOMBRE, U.APATERNO, U.IDROL, R.NOMROL FROM USUARIO U LEFT JOIN ROLES R ON U.IDROL = R.IDROL WHERE U.IDUSER = %s """, (idusuario,))
    usuario = cur.fetchone()

    cur.close()

    return render_template('administrador/nuevoUsuario/editarUsuario.html', roles = roles, usuario = usuario)

#Eliminar Usuario
@app.route('/verUsuarios/eliminar_usuarios/<int:idusuario>')
def eliminar_usuarios(idusuario):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))
    
    # Evitar que el administrador se elimine a sí mismo
    if idusuario == session.get('id'):
        flash("⚠️ No puedes eliminar tu propio usuario.", "error")
        return redirect(url_for('verUsuarios'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM USUARIO WHERE IDUSER = %s', (idusuario,))
    mysql.connection.commit()
    cur.close()

    flash("✅ Usuario eliminado correctamente", "success")

    return redirect(url_for('verUsuarios'))

# MOSTRAR PEDIDOS (solo lectura)
@app.route('/pedidos')
def pedidos():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))    

    cur = mysql.connection.cursor()

    # Obtener todos los pedidos con su estatus y servicio
    cur.execute("""
        SELECT p.IDPEDIDO, p.FECHAENTREGA, e.nomestatus AS ESTATUS, s.NOMSERVICIO,
            CONCAT(u.NOMBRE,' ',u.APATERNO) AS NOMBRE_CLIENTE
        FROM PEDIDOS p
        INNER JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
        INNER JOIN SERVICIOPEDIDO s ON p.IDSERVICIO = s.IDSERVICIO
        INNER JOIN USUARIO u ON p.IDUSER = u.IDUSER
        ORDER BY p.IDPEDIDO ASC
    """)
    pedidos_raw = cur.fetchall()

    pedidos_list = []
    for p in pedidos_raw:
        pedidos_list.append({
            'id': p['IDPEDIDO'],
            'cliente': p['NOMBRE_CLIENTE'],
            'fecha_entrega': p['FECHAENTREGA'],
            'estatus': p['ESTATUS'],
            'servicio': p['NOMSERVICIO']
        })

    cur.close()
    return render_template('administrador/pedidos/pedidos.html', pedidos=pedidos_list)

# EDITAR PEDIDO PURIFICADO
@app.route('/pedidos/editar/<int:idpedido>', methods=['GET', 'POST'])
def editar_pedido(idpedido):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    try:
        cur = mysql.connection.cursor()

        if request.method == 'POST':
            data = request.get_json()
            iduser = data.get('iduser')
            idservicio = data.get('idservicio')
            fecha_entrega = data.get('fecha_entrega')
            prendas = data.get('prendas', [])

            if not iduser or not idservicio or not fecha_entrega or not prendas:
                return jsonify({"success": False, "message": "Faltan datos para actualizar el pedido"}), 400

            # Obtener estado actual
            cur.execute("SELECT IDESTATUS FROM PEDIDOS WHERE IDPEDIDO=%s", (idpedido,))
            pedido_actual = cur.fetchone()
            if not pedido_actual:
                return jsonify({"success": False, "message": "Pedido no encontrado"}), 404
            estado_actual = pedido_actual['IDESTATUS']

            # Calcular totales y agrupar por categoría
            total_peso = 0
            total_costo = 0
            categorias = {}
            for p in prendas:
                cur.execute("""
                    SELECT c.IDCATEGORIA, cat.PRECIOKG
                    FROM CATALOGOPRENDAS c
                    INNER JOIN CATEGORIAPRENDAS cat ON c.IDCATEGORIA = cat.IDCATEGORIA
                    WHERE c.IDCATALOGO = %s
                """, (p['idcatalogo'],))
                cat_info = cur.fetchone()
                if not cat_info:
                    return jsonify({"success": False, "message": f"Prenda ID {p['idcatalogo']} no encontrada"}), 404

                idcat = cat_info['IDCATEGORIA']
                preciokg = float(cat_info['PRECIOKG'])
                categorias.setdefault(idcat, {'peso': 0, 'preciokg': preciokg})
                categorias[idcat]['peso'] += float(p['peso'])
                total_peso += float(p['peso'])

            # Calcular costo total por categoría
            total_costo = sum(info['peso'] * info['preciokg'] for info in categorias.values())

            # Costo adicional por servicio
            cur.execute("SELECT COSTO_KG FROM SERVICIOPEDIDO WHERE IDSERVICIO=%s", (idservicio,))
            servicio = cur.fetchone()
            if servicio:
                total_costo += total_peso * float(servicio['COSTO_KG'])

            # Actualizar pedido
            cur.execute("""
                UPDATE PEDIDOS
                SET IDSERVICIO=%s, IDUSER=%s, FECHAENTREGA=%s, TOTAL=%s, PESOTOTAL=%s
                WHERE IDPEDIDO=%s
            """, (idservicio, iduser, fecha_entrega, total_costo, total_peso, idpedido))

            # Actualizar detalle de prendas
            # Primero, eliminar solo las que ya no estén en el formulario
            cur.execute("SELECT IDCATALOGO FROM PEDIDOS_HAS_CATALOGODETALLE WHERE IDPEDIDO=%s", (idpedido,))
            detalle_existente = {row['IDCATALOGO'] for row in cur.fetchall()}
            detalle_nuevo = {p['idcatalogo'] for p in prendas}

            # Borrar las prendas que ya no están
            for idcat_borrar in detalle_existente - detalle_nuevo:
                cur.execute("DELETE FROM PEDIDOS_HAS_CATALOGODETALLE WHERE IDPEDIDO=%s AND IDCATALOGO=%s",
                            (idpedido, idcat_borrar))

            # Insertar o actualizar las prendas actuales
            for p in prendas:
                if p['idcatalogo'] in detalle_existente:
                    cur.execute("""
                        UPDATE PEDIDOS_HAS_CATALOGODETALLE
                        SET CANTIDAD=%s, PESO=%s
                        WHERE IDPEDIDO=%s AND IDCATALOGO=%s
                    """, (p['cantidad'], p['peso'], idpedido, p['idcatalogo']))
                else:
                    cur.execute("""
                        INSERT INTO PEDIDOS_HAS_CATALOGODETALLE (IDPEDIDO, IDCATALOGO, CANTIDAD, PESO)
                        VALUES (%s, %s, %s, %s)
                    """, (idpedido, p['idcatalogo'], p['cantidad'], p['peso']))

            # Actualizar estado a "En preparación" solo si aún no lo está
            ESTADO_PREPARACION = 2
            if estado_actual != ESTADO_PREPARACION:
                cur.execute("UPDATE PEDIDOS SET IDESTATUS=%s WHERE IDPEDIDO=%s", (ESTADO_PREPARACION, idpedido))

            mysql.connection.commit()
            cur.close()
            return jsonify({"success": True, "message": f"Pedido actualizado. Total: ${total_costo:.2f}"})

        # --- GET: renderizar formulario ---
        cur.execute("SELECT * FROM PEDIDOS WHERE IDPEDIDO=%s", (idpedido,))
        pedido = cur.fetchone()
        if not pedido:
            return "Pedido no encontrado", 404

        cur.execute("SELECT IDUSER, CONCAT(NOMBRE,' ',APATERNO) AS NOMBRE_COMPLETO FROM USUARIO WHERE IDROL = 2")
        clientes = cur.fetchall()

        cur.execute("SELECT IDSERVICIO, NOMSERVICIO, COSTO_KG FROM SERVICIOPEDIDO")
        servicios = cur.fetchall()

        cur.execute("""
            SELECT d.IDCATALOGO, c.NOMBREPRENDA, d.CANTIDAD, d.PESO, cat.IDCATEGORIA, cat.NOMBRE AS NOMBRECATEGORIA
            FROM PEDIDOS_HAS_CATALOGODETALLE d
            INNER JOIN CATALOGOPRENDAS c ON d.IDCATALOGO = c.IDCATALOGO
            INNER JOIN CATEGORIAPRENDAS cat ON c.IDCATEGORIA = cat.IDCATEGORIA
            WHERE d.IDPEDIDO = %s
        """, (idpedido,))
        prendas = cur.fetchall()

        cur.close()
        return render_template('administrador/pedidos/editar_pedido.html',
                            pedido=pedido, clientes=clientes, servicios=servicios, prendas=prendas,
                            current_date=date.today().isoformat())

    except Exception as e:
        mysql.connection.rollback()
        print(f"❌ Error en /pedidos/editar/{idpedido}: {e}")
        return str(e), 500

#Detalles Pedido
@app.route('/pedidos/detalles/<int:idpedido>')
def detalles_pedido(idpedido):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    try:
        # Cursor con diccionarios
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Info general del pedido
        cur.execute("""
            SELECT p.IDPEDIDO, p.FECHAENTREGA, p.IDSERVICIO, e.NOMESTATUS AS ESTATUS,
                s.NOMSERVICIO, CONCAT(u.NOMBRE,' ',u.APATERNO) AS CLIENTE
            FROM PEDIDOS p
            INNER JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
            INNER JOIN SERVICIOPEDIDO s ON p.IDSERVICIO = s.IDSERVICIO
            INNER JOIN USUARIO u ON p.IDUSER = u.IDUSER
            WHERE p.IDPEDIDO = %s
        """, (idpedido,))
        pedido = cur.fetchone()
        if not pedido:
            return jsonify({"success": False, "message": "Pedido no encontrado"}), 404

        # Detalle de prendas
        cur.execute("""
            SELECT c.NOMBREPRENDA AS nombre, d.CANTIDAD AS cantidad, d.PESO AS peso, cat.PRECIOKG AS precio_x_kg
            FROM PEDIDOS_HAS_CATALOGODETALLE d
            INNER JOIN CATALOGOPRENDAS c ON d.IDCATALOGO = c.IDCATALOGO
            INNER JOIN CATEGORIAPRENDAS cat ON c.IDCATEGORIA = cat.IDCATEGORIA
            WHERE d.IDPEDIDO = %s
        """, (idpedido,))
        prendas = cur.fetchall()

        # Totales
        total_peso = sum(float(p['peso']) for p in prendas)
        total_costo = sum(float(p['peso']) * float(p['precio_x_kg']) for p in prendas)

        # Costo adicional por servicio
        cur.execute("SELECT COSTO_KG FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s", (pedido['IDSERVICIO'],))
        servicio = cur.fetchone()
        if servicio:
            total_costo += total_peso * float(servicio['COSTO_KG'])

        cur.close()

        # Devolver JSON para el modal
        return jsonify({
            "success": True,
            "idpedido": pedido['IDPEDIDO'],
            "cliente": pedido['CLIENTE'],
            "fecha_entrega": str(pedido['FECHAENTREGA']),
            "estatus": pedido['ESTATUS'],
            "servicio": pedido['NOMSERVICIO'],
            "prendas": prendas,
            "peso_total": total_peso,
            "costo_total": total_costo
        })

    except Exception as e:
        print(f"❌ Error en /pedidos/detalles/{idpedido}: {e}")
        return jsonify({"success": False, "message": "Error al obtener detalles del pedido", "error": str(e)}), 500

#Eliminar Pedido
@app.route('/pedidos/eliminar_pedido/<int:idpedido>')
def eliminar_pedido(idpedido):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    try: 
        #Instancia de BD
        cur = mysql.connection.cursor()

        #Eliminamos primero la tabla Detalles del pedido
        cur.execute('DELETE FROM PEDIDOS_HAS_CATALOGODETALLE WHERE IDPEDIDO = %s',(idpedido,))

        #Eliminamos el pedido principal
        cur.execute('DELETE FROM PEDIDOS WHERE IDPEDIDO = %s',(idpedido,))

        mysql.connection.commit()
        cur.close()

        return jsonify({"success": True, "message": f"Pedido {idpedido} eliminado correctamente"})
    except Exception as e:
        mysql.connection.rollback()
        print(f"❌ Error al eliminar pedido {idpedido}: {e}")
        return jsonify({"success": False, "message": "Error al eliminar el pedido.", "error": str(e)}), 500

#Nuevo Pedido
@app.route('/nuevoPedido', methods=['GET', 'POST'])
def nuevoPedido():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))
    
    cur = None

    try:
        if request.method == 'POST':
            data = request.get_json()
            iduser = data.get('iduser')
            idservicio = data.get('idservicio')
            fecha_entrega = data.get('fecha_entrega')
            prendas = data.get('prendas', [])

            if not iduser or not idservicio or not fecha_entrega or len(prendas) == 0:
                return jsonify({"success": False, "message": "Faltan datos para crear el pedido"}), 400

            # Calculamos totales por categoría y costo del servicio
            cur = mysql.connection.cursor()
            
            total_peso = 0
            total_costo = 0

            # Diccionario para agrupar por categoria
            categorias = {}
            for p in prendas:
                cur.execute("""
                    SELECT c.IDCATEGORIA, c.NOMBREPRENDA, cat.PRECIOKG
                    FROM CATALOGOPRENDAS c
                    INNER JOIN CATEGORIAPRENDAS cat ON c.IDCATEGORIA = cat.IDCATEGORIA
                    WHERE c.IDCATALOGO = %s
                """, (p['idcatalogo'],))
                cat_info = cur.fetchone()
                if not cat_info:
                    return jsonify({"success": False, "message": f"Prenda ID {p['idcatalogo']} no encontrada"}), 404

                idcat = cat_info['IDCATEGORIA']
                preciokg = float(cat_info['PRECIOKG'])
                nombre_prenda = cat_info['NOMBREPRENDA']

                if idcat not in categorias:
                    categorias[idcat] = {'peso': 0, 'preciokg': preciokg}
                
                categorias[idcat]['peso'] += float(p['peso'])
                total_peso += float(p['peso'])
                p['precio_x_kg'] = preciokg
                p['nombre'] = nombre_prenda


            # Total por categoria
            for cat in categorias.values():
                total_costo += cat['peso'] * cat['preciokg']

            # Costo adicional por servicio
            cur.execute("SELECT NOMSERVICIO, COSTO_KG FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s", (idservicio,))
            servicio = cur.fetchone()
            if servicio:
                total_costo += total_peso * float(servicio['COSTO_KG'])
                nombre_servicio = servicio['NOMSERVICIO']
            else:
                nombre_servicio = "Desconocido"

            # Insertamos PEDIDO
            cur.execute("SELECT MAX(IDPEDIDO) AS max_id FROM PEDIDOS")
            resultado = cur.fetchone()
            idpedido = (resultado['max_id'] or 0) + 1

            cur.execute("""
                INSERT INTO PEDIDOS (IDPEDIDO, IDSERVICIO, IDESTATUS, IDUSER, FECHAENTREGA, TOTAL, PESOTOTAL)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (idpedido, idservicio, 1, iduser, fecha_entrega, total_costo, total_peso))

            # Insertamos detalle de prendas
            for p in prendas:
                cur.execute("""
                    INSERT INTO PEDIDOS_HAS_CATALOGODETALLE (IDPEDIDO, IDCATALOGO, CANTIDAD, PESO)
                    VALUES (%s, %s, %s, %s)
                """, (idpedido, p['idcatalogo'], p['cantidad'], p['peso']))

            mysql.connection.commit()
            
            # Envio de correo al cliente
            try:
                cur.execute("""SELECT CORREO, CONCAT(NOMBRE,' ',APATERNO) AS NOMBRE_COMPLETO
                                FROM USUARIO
                                WHERE IDUSER = %s
                                """, (iduser,))
                user = cur.fetchone()

                if user and user['CORREO']:
                    correo_destino = user['CORREO']
                    nombre_usuario = user['NOMBRE_COMPLETO']

                    enviar_correo_nuevo_pedido(
                        correo_destino=correo_destino,
                        nombre_usuario=nombre_usuario,
                        idpedido=idpedido,
                        fecha_entrega=fecha_entrega,
                        prendas = prendas,
                        peso_total=total_peso,
                        costo_total=total_costo
                    )
            except Exception as mail_error:
                print(f"⚠️ Error al enviar correo: {mail_error}")


            return jsonify({"success": True, "message": f"Pedido registrado. Total: ${total_costo:.2f}", "idpedido": idpedido})

    except Exception as e:
        mysql.connection.rollback()
        print(f"❌ Error en POST /nuevoPedido: {e}")
        return jsonify({"success": False, "message": "Ocurrió un error al guardar el pedido", "error": str(e)}), 500
    
    finally:
        if cur:
            cur.close()

    # GET -> renderizar formulario
    cur = mysql.connection.cursor()

    # Clientes (rol = 2)
    cur.execute("SELECT IDUSER, CONCAT(NOMBRE,' ',APATERNO) AS NOMBRE_COMPLETO FROM USUARIO WHERE IDROL = %s", (2,))
    clientes = cur.fetchall()

    # Servicios
    cur.execute("SELECT IDSERVICIO, NOMSERVICIO, COSTO_KG FROM SERVICIOPEDIDO")
    servicios = cur.fetchall()

    cur.close()
    return render_template('administrador/pedidos/nuevoPedido.html', clientes=clientes, servicios=servicios, current_date=date.today().isoformat())

#Autocompletado Pedido (Nueva Prenda)
@app.route('/buscar_prenda')
def buscar_prenda():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    termino = request.args.get('term', '')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            c.IDCATALOGO,
            c.NOMBREPRENDA,
            cat.IDCATEGORIA,
            cat.NOMBRE AS NOMBRECATEGORIA,
            cat.KGMAXIMO,
            cat.PRECIOKG AS PRECIO_X_KG
        FROM CATALOGOPRENDAS c
        INNER JOIN CATEGORIAPRENDAS cat ON c.IDCATEGORIA = cat.IDCATEGORIA
        WHERE c.NOMBREPRENDA LIKE %s
        LIMIT 10
    """, ('%' + termino + '%',))
    prendas = cur.fetchall()
    cur.close()

    #Formato para JS
    data_para_js = [
        {
            'id': p['IDCATALOGO'],
            'nombre': p['NOMBREPRENDA'],
            'idcategoria': p['IDCATEGORIA'],
            'categoria': p['NOMBRECATEGORIA'],
            'kgmaximo': float(p['KGMAXIMO']),
            'precio_kg': float(p['PRECIO_X_KG'])
        }
        for p in prendas
    ]

    return Response(json.dumps(data_para_js), mimetype='application/json')

#Cambio Estado de Pedido
@app.route('/cambioEstadoPedido', methods=['GET', 'POST'])
def cambioEstadoPedido():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()  # cursor normal o dict cursor, soporta ambos

    if request.method == 'POST':
        try:
            data = request.get_json()
            print("📦 Datos recibidos:", data)

            if not data or 'id_pedido' not in data or 'nuevo_estatus' not in data:
                return jsonify({"success": False, "msg": "Datos incompletos"}), 400

            id_pedido = data['id_pedido']
            nuevo_estatus = int(str(data['nuevo_estatus']).strip())

            # === Verificar si el pedido existe ===
            cur.execute("SELECT IDESTATUS FROM PEDIDOS WHERE IDPEDIDO = %s", (id_pedido,))
            pedido = cur.fetchone()

            if not pedido:
                cur.close()
                return jsonify({"success": False, "msg": "Pedido no encontrado"}), 404

            estatus_actual = (
                int(pedido['IDESTATUS']) if isinstance(pedido, dict)
                else int(pedido[0])
            )
            print(f"🔹 Estatus actual del pedido {id_pedido}: {estatus_actual}")

            # === Validaciones ===
            if estatus_actual == 3:
                cur.close()
                return jsonify({"success": False, "msg": "El pedido ya está 'Listo'"}), 400

            if nuevo_estatus != estatus_actual + 1:
                cur.close()
                return jsonify({"success": False, "msg": "Solo se puede avanzar un nivel"}), 400

            # === Iniciar transacción ===
            mysql.connection.begin()
            cur.execute("UPDATE PEDIDOS SET IDESTATUS = %s WHERE IDPEDIDO = %s", (nuevo_estatus, id_pedido))
            print(f"✅ Pedido {id_pedido} actualizado temporalmente a estatus {nuevo_estatus}")

            # === Si pasa de "En espera" (1) a "En preparación" (2) ===
            if nuevo_estatus == 2:
                print("🧮 Descontando materia prima...")

                cur.execute("""
                    SELECT cd.IDCATALOGO, cd.CANTIDAD, cd.PESO, cp.IDCATEGORIA
                    FROM PEDIDOS_HAS_CATALOGODETALLE cd
                    JOIN CATALOGOPRENDAS cp ON cd.IDCATALOGO = cp.IDCATALOGO
                    WHERE cd.IDPEDIDO = %s
                """, (id_pedido,))
                prendas = cur.fetchall()

                if prendas:
                    peso_por_categoria = {}
                    for p in prendas:
                        id_cat = p['IDCATEGORIA'] if isinstance(p, dict) else p[3]
                        peso = float(p['PESO'] if isinstance(p, dict) else p[2] or 0)
                        peso_por_categoria[id_cat] = peso_por_categoria.get(id_cat, 0) + peso

                    print("📊 Peso por categoría:", peso_por_categoria)
                    faltantes = []

                    for id_categoria, peso_total in peso_por_categoria.items():
                        cur.execute("SELECT KGMAXIMO FROM CATEGORIAPRENDAS WHERE IDCATEGORIA = %s", (id_categoria,))
                        cat_data = cur.fetchone()
                        if not cat_data:
                            continue

                        kgmaximo = float(cat_data['KGMAXIMO'] if isinstance(cat_data, dict) else cat_data[0])
                        cargas = ceil(peso_total / kgmaximo)  # ✅ Corrección aquí
                        print(f"➡️ Categoría {id_categoria}: {peso_total} kg -> {cargas} carga(s)")

                        # === Obtener materiales ===
                        cur.execute("""
                            SELECT c.IDMATERIAPRIMA, c.DESCPORCARGA, m.NOMBREMATERIAPRIMA,
                                m.CANTIDAD, m.CANTIDADUM, u.NOMBRE AS UNIDAD
                            FROM CARGAS c
                            JOIN MATERIAPRIMA m ON c.IDMATERIAPRIMA = m.IDMATERIAPRIMA
                            JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
                            WHERE c.IDCATEGORIA = %s
                        """, (id_categoria,))
                        materiales = cur.fetchall()

                        for mat in materiales:
                            id_mat = mat['IDMATERIAPRIMA'] if isinstance(mat, dict) else mat[0]
                            desc_por_carga = float(mat['DESCPORCARGA'] if isinstance(mat, dict) else mat[1])
                            nombre_mp = mat['NOMBREMATERIAPRIMA'] if isinstance(mat, dict) else mat[2]
                            cantidad_actual = float(mat['CANTIDAD'] if isinstance(mat, dict) else mat[3])
                            cantidad_um = float(mat['CANTIDADUM'] if isinstance(mat, dict) else mat[4])
                            unidad = mat['UNIDAD'] if isinstance(mat, dict) else mat[5]
                            total_descuento = desc_por_carga * cargas

                            if cantidad_actual < total_descuento:
                                faltantes.append({
                                    "nombre": nombre_mp,
                                    "unidad": unidad,
                                    "faltante": round(total_descuento - cantidad_actual, 2),
                                    "disponible": round(cantidad_actual, 2),
                                    "requerido": round(total_descuento, 2)
                                })
                            else:
                                cur.execute("""
                                    UPDATE MATERIAPRIMA
                                    SET CANTIDAD = CANTIDAD - %s
                                    WHERE IDMATERIAPRIMA = %s
                                """, (total_descuento, id_mat))

                    # === Si hay faltantes ===
                    if faltantes:
                        print("🚫 Materia prima insuficiente, realizando rollback...")
                        mysql.connection.rollback()
                        cur.execute("UPDATE PEDIDOS SET IDESTATUS = %s WHERE IDPEDIDO = %s", (estatus_actual, id_pedido))
                        mysql.connection.commit()
                        cur.close()

                        mensaje = "⚠️ No hay suficiente materia prima:\n"
                        for f, mat in zip(faltantes, materiales):
                            cantidad_um = float(mat['CANTIDADUM'] if isinstance(mat, dict) else mat[4])
                            unidad_real = mat['UNIDAD'] if isinstance(mat, dict) else mat[5]  # Litros, Mililitros, etc.

                            # Definir unidad pequeña para mostrar "faltan X"
                            if unidad_real.lower() == 'litros':
                                factor = 1000
                                unidad_mg = 'Mililitros'
                            elif unidad_real.lower() == 'kilogramos':
                                factor = 1000
                                unidad_mg = 'Miligramos'
                            else:
                                factor = 1
                                unidad_mg = unidad_real

                            faltante_convertido = f['faltante'] * factor
                            requerido_convertido = f['requerido'] * factor
                            disponible_convertido = f['disponible'] * factor

                            # Siempre mostramos que falta 1 unidad completa
                            unidades_faltantes = 1

                            mensaje += (
                                f"- {f['nombre']}: disponibles {disponible_convertido:.0f} / "
                                f"requeridos {requerido_convertido:.0f} {unidad_mg} "
                                f"({faltante_convertido:.0f} {unidad_mg} faltan, "
                                f"falta {unidades_faltantes} {f['nombre']} de {cantidad_um} {unidad_real})\n"
                            )



                        return jsonify({"success": False, "msg": mensaje}), 400

            # === Confirmar cambios ===
            mysql.connection.commit()
            print("✅ Pedido actualizado correctamente.")

            # Enviar el correo
            try:
                cur.execute("""
                    SELECT u.CORREO, CONCAT(u.NOMBRE, ' ', u.APATERNO) AS NOMBRE_COMPLETO,
                            p.FECHAENTREGA, p.TOTAL, p.PESOTOTAL
                    FROM USUARIO u
                    JOIN PEDIDOS p ON u.IDUSER = p.IDUSER
                    WHERE p.IDPEDIDO = %s
                    """, (id_pedido,))
                user = cur.fetchone()

                if user and user['CORREO']:
                    correo_destino = user['CORREO']
                    nombre_usuario = user['NOMBRE_COMPLETO']
                    fecha_entrega = user['FECHAENTREGA']
                    total_costo = user['TOTAL']
                    total_peso = user['PESOTOTAL']

                    # Obtener prendas del pedido
                    cur.execute("""
                                SELECT cd.IDCATALOGO, cp.NOMBREPRENDA, cd.CANTIDAD, cd.PESO, cd.PRECIO_X_KG
                                FROM PEDIDOS_HAS_CATALOGODETALLE cd
                                JOIN CATALOGOPRENDAS cp ON cd.IDCATALOGO = cp.IDCATALOGO
                                WHERE cd.IDPEDIDO = %s
                                """, (id_pedido,))
                    prendas = cur.fetchall()

                    # Obtener Estatus
                    estatus_texto = None
                    cur.execute("SELECT NOMESTATUS FROM ESTATUSPEDIDO WHERE IDESTATUS = %s", (nuevo_estatus,))
                    estatus_info = cur.fetchone()
                    if estatus_info:
                        estatus_texto = estatus_info['NOMESTATUS']
                    
                    enviar_correo_cambio_estatus(
                        correo_destino=correo_destino,
                        nombre_usuario=nombre_usuario,
                        idpedido=id_pedido,
                        fecha_entrega=fecha_entrega,
                        estatus=estatus_texto,
                        prendas=prendas,
                        peso_total=total_peso,
                        costo_total=total_costo
                    )
            except Exception as mail_error:
                print(f"⚠️ Error enviando correo de cambio de estatus: {mail_error}")
            
            cur.close()
            
            return jsonify({"success": True, "msg": "Estado actualizado correctamente."})

        except Exception as e:
            import traceback
            traceback.print_exc()
            mysql.connection.rollback()
            return jsonify({"success": False, "msg": f"Error interno del servidor: {str(e)}"}), 500

    # === GET ===
    id_buscar = request.args.get('id_pedido', '')
    base_query = """
        SELECT 
            p.IDPEDIDO,
            CONCAT(u.NOMBRE, ' ', u.APATERNO) AS NOMBRECLIENTE,
            p.IDESTATUS,
            e.NOMESTATUS,
            p.FECHAENTREGA
        FROM PEDIDOS p
        JOIN USUARIO u ON p.IDUSER = u.IDUSER
        JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
    """
    params = ()
    if id_buscar:
        base_query += " WHERE p.IDPEDIDO LIKE %s OR CONCAT(u.NOMBRE, ' ', u.APATERNO) LIKE %s"
        params = ('%' + id_buscar + '%', '%' + id_buscar + '%')

    base_query += """
        ORDER BY 
            CASE 
                WHEN p.IDESTATUS = 2 THEN 0
                WHEN p.IDESTATUS = 1 THEN 1
                WHEN p.IDESTATUS = 3 THEN 2
                ELSE 3 
            END, 
            p.FECHAENTREGA ASC
    """

    cur.execute(base_query, params)
    pedidos = cur.fetchall()

    cur.execute("SELECT IDESTATUS, NOMESTATUS FROM ESTATUSPEDIDO ORDER BY IDESTATUS")
    estatus_list = cur.fetchall()
    cur.close()

    return render_template(
        'administrador/cambioEstadoPedido.html',
        pedidos=pedidos,
        estatus_list=estatus_list,
        id_buscar=id_buscar
    )

# Nuevo Proveedor
@app.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST' and 'nombre' in request.form and 'correo' in request.form and 'telefono' in request.form:
        
        #Capturamos los datos obtenidos en el form
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']

        #Creamos instancia en la BD para generar consultas
        cur = mysql.connection.cursor()

        #Obtener el ultimo ID insertado en la BD
        cur.execute('SELECT MAX(IDPROVEEDOR) AS max_id FROM PROVEEDORES')
        result = cur.fetchone()
        id = (result['max_id'] or 0) + 1

        #Generamos insert en la tabla Proveedores
        cur.execute('INSERT INTO PROVEEDORES (IDPROVEEDOR, NOMBREPROVEEDOR, CORREO, TELEFONO) VALUES (%s,%s,%s,%s)',(id, nombre, correo, telefono))

        #Generamoa el comit del insert
        mysql.connection.commit()

        #Cerramos la BD
        cur.close()

        #Enviamos mensaje de éxito
        flash("✅Nuevo proveedor ingresado con éxito", "success")

        return redirect(url_for('proveedores'))
    
    #Consultas GET
    cur = mysql.connection.cursor()

    #Capturamos nombre ingresado en la barra de busqueda
    nombre_buscar = request.args.get('buscar-nombre', '')

    #Verificamos si se ingreso algo en la barra de busqueda
    if nombre_buscar:
        #Buscamos el dato especifico
        cur.execute('SELECT IDPROVEEDOR, NOMBREPROVEEDOR FROM PROVEEDORES WHERE NOMBREPROVEEDOR LIKE %s', ('%' + nombre_buscar + '%',))
    else: #Si no ingreso nada en la barra, entonces mostramos los datos existentes de proveedores
        cur.execute('SELECT IDPROVEEDOR, NOMBREPROVEEDOR FROM PROVEEDORES')

    #Se guarda en proveedores el valor ya sea de la barra de busqueda ó los datos generales
    proveedores = cur.fetchall()
    cur.close()
    return render_template('administrador/proveedores/proveedores.html', proveedores=proveedores, nombre_buscar = nombre_buscar)

# Editar Proveedor
@app.route('/proveedores/editar/<int:idproveedor>', methods=['GET', 'POST'])
def editar_proveedor(idproveedor):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST':
        #Capturamos los datos
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']

        #Creamos instancia de la BD
        cur = mysql.connection.cursor()

        cur.execute('UPDATE PROVEEDORES SET NOMBREPROVEEDOR = %s, CORREO = %s, TELEFONO = %s WHERE IDPROVEEDOR = %s', (nombre, correo, telefono, idproveedor))

        #Guardamos el UPDATE
        mysql.connection.commit()

        #Cerramos la BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Dato actualizado correctamente", "success")
        return redirect(url_for('proveedores'))
    #Si es GET
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM PROVEEDORES WHERE IDPROVEEDOR=%s',(idproveedor,))
    proveedor = cur.fetchone()
    cur.close()

    return render_template('administrador/proveedores/editarProveedor.html', proveedor = proveedor)

# Eliminar Proveedor
@app.route('/proveedores/eliminar/<int:idproveedor>')
def eliminar_proveedor(idproveedor):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM PROVEEDORES WHERE IDPROVEEDOR = %s', (idproveedor,))
    mysql.connection.commit()
    cur.close()
    flash('✅ Proveedor eliminado correctamente','success')
    return redirect(url_for('proveedores'))

# Compra Materia Prima
@app.route('/compraMateriaPrima', methods=['GET', 'POST'])
def compraMateriaPrima():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST':
        try:
            # === DATOS DE COMPRA GENERAL ===
            idproveedor = request.form.get('proveedor')
            fecha = request.form.get('fecha')
            iduser = session.get('id')  # ID del usuario logueado

            if not (idproveedor and fecha and iduser):
                flash('Campos obligatorios.', 'danger')
                return redirect(url_for('compraMateriaPrima'))

            cur = mysql.connection.cursor()

            # Obtener el próximo ID de compra
            cur.execute('SELECT MAX(IDCOMPRA) AS max_id FROM COMPRAMATERIAPRIMA')
            resultado = cur.fetchone()
            idcompra = (resultado['max_id'] or 0) + 1

            # Iniciar transacción
            mysql.connection.begin()

            # Insertar compra general
            cur.execute('''
                INSERT INTO COMPRAMATERIAPRIMA (IDCOMPRA, IDUSER, IDPROVEEDOR, FECHA)
                VALUES (%s, %s, %s, %s)
            ''', (idcompra, iduser, idproveedor, fecha))

            # === DATOS DETALLE ===
            detalle = request.form.to_dict(flat=False)
            nombres = detalle.get('detalle[][nombre]', [])
            cantidades = detalle.get('detalle[][cantidad]', [])
            unidades = detalle.get('detalle[][unidad]', [])      # NUEVO CAMPO
            cant_um = detalle.get('detalle[][cantidadum]', [])    # NUEVO CAMPO

            if not nombres or not cantidades or not unidades or not cant_um:
                flash('No se ingresaron productos al detalle.', 'danger')
                mysql.connection.rollback()
                cur.close()
                return redirect(url_for('compraMateriaPrima'))

            # Insertar cada detalle
            for nombre, cantidad, unidad, cantidadum in zip(nombres, cantidades, unidades, cant_um):
                # Buscar el producto exacto en MATERIAPRIMA
                cur.execute('''
                    SELECT m.IDMATERIAPRIMA, m.CANTIDAD
                    FROM MATERIAPRIMA m
                    JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
                    WHERE m.NOMBREMATERIAPRIMA = %s
                    AND m.CANTIDADUM = %s
                    AND u.NOMBRE = %s
                ''', (nombre, cantidadum, unidad))

                resultado = cur.fetchone()

                if not resultado:
                    flash(f'El producto "{nombre} {cantidadum} {unidad}" no existe en la base de datos.', 'danger')
                    mysql.connection.rollback()
                    cur.close()
                    return redirect(url_for('compraMateriaPrima'))

                id_materia = resultado['IDMATERIAPRIMA']
                stock_actual = resultado['CANTIDAD']

                # Obtener último IDDETALLE
                cur.execute('SELECT MAX(IDDETALLE) AS max_id FROM COMPRADETALLE')
                existente = cur.fetchone()
                iddetalle = (existente['max_id'] or 0) + 1

                # Insertar detalle
                cur.execute('''
                    INSERT INTO COMPRADETALLE (IDDETALLE, IDCOMPRA, IDMATERIAPRIMA, CANTIDAD)
                    VALUES (%s, %s, %s, %s)
                ''', (iddetalle, idcompra, id_materia, cantidad))

                # Actualizar stock de materia prima
                nuevo_stock = stock_actual + int(cantidad)
                cur.execute('''
                    UPDATE MATERIAPRIMA
                    SET CANTIDAD = %s
                    WHERE IDMATERIAPRIMA = %s
                ''', (nuevo_stock, id_materia))

            # Commit de todas las transacciones
            mysql.connection.commit()
            cur.close()
            flash('Compra registrada correctamente.', 'success')
            return redirect(url_for('compraMateriaPrima'))

        except Exception as e:
            print(f"❌ Error en POST /compraMateriaPrima: {e}")
            mysql.connection.rollback()
            flash('Ocurrió un error al registrar la compra. Ningún cambio fue guardado.', 'danger')
            return redirect(url_for('compraMateriaPrima'))

    # === GET ===
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDPROVEEDOR, NOMBREPROVEEDOR FROM PROVEEDORES')
    proveedores = cur.fetchall()

    iduser = session['id']
    cur.execute('SELECT NOMBRE, APATERNO FROM USUARIO WHERE IDUSER = %s', (iduser,))
    empleado = cur.fetchone()
    cur.close()

    return render_template('administrador/compraMateriaPrima.html', proveedores=proveedores, empleado=empleado)

#Compra Materia Prima (autocompletado Materia Prima - Detalle Compra)
@app.route('/buscar_producto')
def buscar_producto():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    termino = request.args.get('term', '') # term = Clave que se espera en el FRONTEND, y (' ') es el valor que se guardará en (term)

    cur = mysql.connection.cursor() #Instancia BD

    #LIMIT 10 indica que permitirá máximo 10 resultados
    cur.execute('''
        SELECT m.NOMBREMATERIAPRIMA, u.NOMBRE AS UNIDAD, m.CANTIDADUM
        FROM MATERIAPRIMA m
        JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
        WHERE m.NOMBREMATERIAPRIMA LIKE %s
        LIMIT 10
    ''', ('%' + termino + '%',))

    productos = cur.fetchall()

    cur.close()

    #Retornar un JSON simple
    #Originalmente productos = [{'NOMBREMATERIAPRIMA':'Cloro'}, {'NOMBREMATERIAPRIMA':'Jabon'}]
    #p['NOMBREMATERIAPRIMA'] for p in productos] obtendrá solo el nombre ['Cloro', 'Jabon']
    #Json.dumps convierte la lista en un JSON
    #mimetype le dice al navegador que interprete los datos como un JSON

    sugerencias = [
    f"{p['NOMBREMATERIAPRIMA']} {int(p['CANTIDADUM']) if p['CANTIDADUM'] % 1 == 0 else p['CANTIDADUM']} {p['UNIDAD']}"
    for p in productos
    ]

    return Response(json.dumps(sugerencias), mimetype='application/json')

#Catalogo Productos
@app.route('/catalogoProductos')
def catalogoProductos():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    #Crear instancia de BD
    cur = mysql.connection.cursor()

    #Obtener consulta
    cur.execute(""" SELECT 
                        c.NOMBRE AS categoria,
                        m.NOMBREMATERIAPRIMA AS nombre_producto,
                        m.CANTIDAD AS existencia,
                        u.NOMBRE AS unidad,
                        ca.DESCPORCARGA AS por_carga
                    FROM CARGAS ca
                    INNER JOIN CATEGORIAPRENDAS c ON ca.IDCATEGORIA = c.IDCATEGORIA
                    INNER JOIN MATERIAPRIMA m ON ca.IDMATERIAPRIMA = m.IDMATERIAPRIMA
                    INNER JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
                    ORDER BY c.NOMBRE, m.NOMBREMATERIAPRIMA;""")
    productos = cur.fetchall()
    cur.close()

    #Convertimos la lista en diccionario legible para Jinja2
    lista_productos = [] #Definimos un arreglo
    for p in productos: #Obtenemos cada dato de productos con un arreglo
        lista_productos.append({
            'categoria': p['categoria'],
            'nombre': p['nombre_producto'],
            'existencia': p['existencia'],
            'unidad': p['unidad'],
            'por_carga':p['por_carga']
        })

    return render_template('administrador/catalogoProductos.html', productos = lista_productos)

#Nueva Categoría de Prenda
@app.route('/categoriaPrendas', methods=['GET', 'POST'])
def categoriaPrendas():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST' and 'nombre' in request.form and 'kgmaximo' in request.form and 'preciokg' in request.form:
        #Capturar los datos ingresados en el form
        #Convertimos los valores en minusculas
        nombre = request.form['nombre'].strip()
        kgmaximo = request.form['kgmaximo']
        preciokg = request.form['preciokg']

        #Crear instancia BD
        cur = mysql.connection.cursor()

        #Verificar que el dato a crear no exista en la bd
        cur.execute('SELECT * FROM CATEGORIAPRENDAS WHERE LOWER(NOMBRE) =  %s',(nombre.lower(),))
        existente = cur.fetchone()

        #Si existe,enviamos mensaje de error
        if existente:
            flash("❌La categoría ya existe", "danger")
            return redirect(url_for('categoriaPrendas'))
        
        #Si no existe,obtener ultimo ID de categoria prendas
        cur.execute('SELECT MAX(IDCATEGORIA) AS max_id FROM CATEGORIAPRENDAS')
        result = cur.fetchone()
        id = (result['max_id'] or 0) + 1

        #Generamos INSERT
        cur.execute('INSERT INTO CATEGORIAPRENDAS(IDCATEGORIA, NOMBRE, KGMAXIMO, PRECIOKG) VALUES (%s, %s, %s, %s)',(id, nombre, kgmaximo, preciokg),)

        #Generamos COMMIT
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Categoria de prendas creada de manera éxitosa", "success")

        return redirect(url_for('categoriaPrendas'))
    
    #Si no es metodo POST, y es método GET mostrar los datos existentes
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDCATEGORIA, NOMBRE FROM CATEGORIAPRENDAS')
    categorias = cur.fetchall()

    return render_template('/administrador/categoriaPrendas/categoriaPrendas.html', categorias = categorias)

#Editar Categoría de Prenda
@app.route('/categoriaPrenda/editar_categoria/<int:idcategoria>', methods=['GET', 'POST'])
def editar_categoria(idcategoria):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    #Verificar que el formulario se haya enviado
    if request.method == 'POST':
        
        #Capturamos los datos ingresados
        nombre = request.form['nombre']
        kgmaximo = request.form['kgmaximo']
        preciokg = request.form['preciokg']

        #Creamos instancia BD
        cur = mysql.connection.cursor()

        #Generamos UPDATE
        cur.execute('UPDATE CATEGORIAPRENDAS SET NOMBRE = %s, KGMAXIMO = %s, PRECIOKG = %s WHERE IDCATEGORIA = %s',(nombre, kgmaximo, preciokg, idcategoria))

        #Guardamos UPDATE
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Enviamos mensaje de éxito
        flash("✅ Dato actualizado correctamente", "success")
        return redirect(url_for('categoriaPrendas'))
    
    #Si es GET, solo mostramos los datos a actualizar
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDCATEGORIA, NOMBRE FROM CATEGORIAPRENDAS WHERE IDCATEGORIA = %s', (idcategoria,))
    categoria = cur.fetchone()
    cur.close()
    
    return render_template('/administrador/categoriaPrendas/editarCategoriaPrendas.html', categoria = categoria)

#Eliminar Categoría de Prenda
@app.route('/categoriaPrenda/eliminar_categoria/<int:idcategoria>')
def eliminar_categoria(idcategoria):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM CATEGORIAPRENDAS WHERE IDCATEGORIA = %s', (idcategoria,))
    mysql.connection.commit()
    cur.close()

    flash("✅ Categoría eliminada correctamente", "success")
    return redirect(url_for('categoriaPrendas'))

#Nueva Prenda
@app.route('/catalogoPrendas', methods=['GET', 'POST'])
def catalogoPrendas():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST':
        try:
            #Obtener los datos del FORM Nueva Prenda
            nombre = request.form['nombre']
            idcategoria = request.form['categoria']
            iduser = session.get('id') #ID del usuario logueado

            # Validación de los campos
            if not (nombre and idcategoria and iduser):
                flash("Campos obligatorios", "danger")
                return redirect(url_for('catalogoPrendas'))
            
            #Creamos intancia BD
            cur = mysql.connection.cursor()

            #Obtener ID
            cur.execute('SELECT MAX(IDCATALOGO) AS max_id FROM CATALOGOPRENDAS')
            resultado = cur.fetchone()
            idprenda = (resultado['max_id'] or 0) + 1

            #Generamos INSERT
            cur.execute('INSERT INTO CATALOGOPRENDAS(IDCATALOGO, IDCATEGORIA, NOMBREPRENDA, PRECIO) VALUES(%s, %s, %s, %s)',(idprenda, idcategoria, nombre, 0))

            #Guardamos COMMIT
            mysql.connection.commit()

            #Cerramos BD
            cur.close()

            #Mensaje de éxito
            flash("Nueva prenda exitosa", "success")
            return redirect(url_for('catalogoPrendas'))

        except Exception as e:
            flash(f"Error: {str(e)}", "e")
            return redirect(url_for('catalogoPrendas'))
    
    #Si es GET, mostrar los campos
    cur = mysql.connection.cursor()

    #Obtenemos las categorias
    cur.execute('SELECT IDCATEGORIA, NOMBRE FROM CATEGORIAPRENDAS')
    categorias = cur.fetchall()

    #Obtenemos el usuario logueado
    iduser = session.get('id') 
    cur.execute('SELECT IDUSER, NOMBRE, APATERNO FROM USUARIO WHERE IDUSER = %s', (iduser,))
    empleado = cur.fetchone()

    #Obtenemos prendas con precio de la categoría
    cur.execute('''
        SELECT p.IDCATALOGO, p.NOMBREPRENDA AS nombre, c.NOMBRE AS categoria, c.PRECIOKG AS precio_categoria
        FROM CATALOGOPRENDAS p
        LEFT JOIN CATEGORIAPRENDAS c ON p.IDCATEGORIA = c.IDCATEGORIA
    ''')
    prendas = cur.fetchall()

    # Calcular siguiente ID para mostrar (aunque no se use en el form)
    cur.execute('SELECT MAX(IDCATALOGO) AS max_id FROM CATALOGOPRENDAS')
    resultado = cur.fetchone()
    idprenda = (resultado['max_id'] or 0) + 1

    cur.close()
    return render_template('administrador/prendas/catalogoPrendas.html', idprenda = idprenda, categorias = categorias, empleado = empleado, prendas = prendas)

#Editar Prenda
@app.route('/catalogoPrendas/editar_prenda/<int:idcatalogo>', methods=['GET', 'POST'])
def editar_prenda(idcatalogo):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST':
        #Capturamos nuevo FORM
        nombre = request.form['nombre']
        categoria = request.form['categoria']

        #Crear instancia BD
        cur = mysql.connection.cursor()

        #Generar UPDATE
        cur.execute('UPDATE CATALOGOPRENDAS SET IDCATEGORIA = %s, NOMBREPRENDA = %s WHERE IDCATALOGO = %s',(categoria, nombre, idcatalogo))

        #Guardar UPDATE
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Prenda actualizada correctamente", "success")

        return redirect(url_for('catalogoPrendas'))
    
    #Si es GET, mostramos datos a editar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM CATALOGOPRENDAS WHERE IDCATALOGO = %s", (idcatalogo,))
    prenda = cur.fetchone()

    # Consultar categorías para el select
    cur.execute("SELECT * FROM CATEGORIAPRENDAS")
    categorias = cur.fetchall()
    cur.close()

    return render_template('administrador/prendas/editarPrenda.html', prenda = prenda, categorias = categorias)

#Eliminar Prenda
@app.route('/catalogoPrendas/eliminar_prenda/<int:idcatalogo>')
def eliminar_prenda(idcatalogo):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM CATALOGOPRENDAS WHERE IDCATALOGO = %s',(idcatalogo,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Prenda eliminada correctamente", "success")

    return redirect(url_for('catalogoPrendas'))

# ===== Conversión de cantidad por carga a unidad base según dígitos =====
def convertir_carga_a_base(cantidad):
    """
    Convierte la cantidad ingresada en 'Cantidad por carga' a la unidad base
    según la cantidad de dígitos:
    - 3 dígitos → mililitros o gramos → dividir entre 1000
    - 1 dígito  → litros o kilogramos → mantener igual
    """
    cantidad_str = str(cantidad).strip()
    if len(cantidad_str) == 3:
        return float(cantidad_str) / 1000  # 3 dígitos → mililitros o gramos
    elif len(cantidad_str) == 1:
        return float(cantidad_str)  # 1 dígito → litros o kilogramos
    else:
        raise ValueError("Solo se permiten cantidades de 1 o 3 dígitos para la carga")

# ===== RUTA COMPLETA: CARGAS =====
@app.route('/cargas', methods=['GET', 'POST'])
def cargas():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        idcategoria = request.form['idcategoria']
        id_materias_list = request.form.getlist('idmateria')
        cargas_list = request.form.getlist('carga')

        if not idcategoria or not id_materias_list:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('cargas'))

        exitosas = 0
        fallidas = 0

        for id_materia, carga_cantidad in zip(id_materias_list, cargas_list):
            try:
                id_materia = int(id_materia)
                carga_int = int(float(carga_cantidad))  # Entero para mostrar en input
                carga_base = convertir_carga_a_base(carga_int)  # Convertir a unidad base
                id_categoria_int = int(idcategoria)
            except ValueError:
                fallidas += 1
                continue

            # Obtener último ID
            cur.execute('SELECT MAX(IDCLAVE) AS max_id FROM CARGAS')
            resultado = cur.fetchone()
            idclave = (resultado['max_id'] or 0) + 1

            # Insertar en la tabla CARGAS
            cur.execute('INSERT INTO CARGAS(IDCLAVE, IDCATEGORIA, IDMATERIAPRIMA, DESCPORCARGA) VALUES (%s, %s, %s, %s)',
                        (idclave, id_categoria_int, id_materia, carga_base))
            exitosas += 1

        mysql.connection.commit()

        if exitosas > 0:
            flash(f"Registro de Carga(s) exitoso. Se insertaron {exitosas} fila(s).", "success")
        if fallidas > 0 and exitosas == 0:
            flash(f"No se pudo registrar ninguna carga. Revisa las advertencias.", "danger")

        return redirect(url_for('cargas'))

    # ===== GET: Mostrar cargas existentes =====
    cur.execute('''
        SELECT 
            c.IDCLAVE,
            c.IDCATEGORIA,
            cat.NOMBRE AS CATEGORIA,
            m.NOMBREMATERIAPRIMA,
            m.CANTIDADUM,
            u.NOMBRE AS UNIDAD,
            c.DESCPORCARGA
        FROM CARGAS c
        JOIN CATEGORIAPRENDAS cat ON cat.IDCATEGORIA = c.IDCATEGORIA
        JOIN MATERIAPRIMA m ON m.IDMATERIAPRIMA = c.IDMATERIAPRIMA
        JOIN UNIDADESMEDIDA u ON u.IDUNIDAD = m.IDUNIDAD
        ORDER BY cat.NOMBRE ASC, c.IDCLAVE ASC
    ''')

    cargas = cur.fetchall()

    # Función para formatear cantidad por carga
    def formatear_carga(desc_carga):
        if desc_carga < 1:
            return int(desc_carga * 1000)  # multiplicar por 1000 si es <1
        return int(desc_carga)  # si >=1 mostrar entero

    # Preparar datos legibles
    cargas_mostrar = []
    for c in cargas:
        cantidadum = float(c['CANTIDADUM'])
        unidad = c['UNIDAD']
        if unidad.lower() in ['mililitros', 'gramos', 'miligramos']:
            cantidad_display = cantidadum * 1000
        else:
            cantidad_display = cantidadum
        materia_display = f"{c['NOMBREMATERIAPRIMA']} {int(cantidad_display)} {unidad}"

        carga_display = formatear_carga(float(c['DESCPORCARGA']))

        cargas_mostrar.append({
            'IDCLAVE': c['IDCLAVE'],
            'IDCATEGORIA': c['IDCATEGORIA'],
            'CATEGORIA': c['CATEGORIA'],
            'MATERIA': materia_display,
            'DESCPORCARGA': carga_display
        })

    # Agrupar por categoría para rowspan
    cargas_agrupadas = {}
    categorias_con_carga = set()
    for c in cargas_mostrar:
        cat = c['CATEGORIA']
        if cat not in cargas_agrupadas:
            cargas_agrupadas[cat] = []
        cargas_agrupadas[cat].append(c)
        categorias_con_carga.add(c['CATEGORIA'])

    # Categorías sin carga
    cur.execute('SELECT IDCATEGORIA, NOMBRE FROM CATEGORIAPRENDAS ORDER BY NOMBRE ASC')
    todas_categorias = cur.fetchall()
    categorias = [cat for cat in todas_categorias if cat['NOMBRE'] not in categorias_con_carga]

    # Materias primas
    cur.execute('SELECT IDMATERIAPRIMA, NOMBREMATERIAPRIMA, CANTIDADUM, IDUNIDAD FROM MATERIAPRIMA ORDER BY NOMBREMATERIAPRIMA ASC')
    materias = cur.fetchall()

    cur.close()

    return render_template(
        'administrador/cargas/cargas.html',
        cargas_agrupadas=cargas_agrupadas,
        categorias=categorias,
        materias=materias
    )

# AUTOCOMPLETADO MATERIA PRIMA
@app.route('/buscar_materia')
def buscar_materia():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    termino = request.args.get('term', '')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            m.IDMATERIAPRIMA,
            CONCAT(
                m.NOMBREMATERIAPRIMA, ' ',
                TRIM(TRAILING '.00' FROM 
                    (CASE 
                        WHEN m.CANTIDADUM = FLOOR(m.CANTIDADUM) THEN CAST(FORMAT(m.CANTIDADUM, 0) AS CHAR)
                        ELSE CAST(m.CANTIDADUM AS CHAR)
                    END)
                ), ' ',
                (CASE 
                    WHEN m.CANTIDADUM = 1 THEN 
                        TRIM(TRAILING 's' FROM u.NOMBRE)
                    ELSE 
                        u.NOMBRE
                END)
            ) AS NOMBRE_COMPLETO
        FROM MATERIAPRIMA m
        JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
        WHERE CONCAT(m.NOMBREMATERIAPRIMA, ' ', m.CANTIDADUM, ' ', u.NOMBRE) LIKE %s
        ORDER BY m.NOMBREMATERIAPRIMA ASC
        LIMIT 10
    """, ('%' + termino + '%',))
    materias = cur.fetchall()
    cur.close()
    data_para_js = [{'id': m['IDMATERIAPRIMA'], 'nombre': m['NOMBRE_COMPLETO']} for m in materias]
    return Response(json.dumps(data_para_js), mimetype='application/json')

# ===== RUTA: EDITAR CARGA =====
@app.route('/cargas/editar_carga/<int:idcategoria>', methods=['GET', 'POST'])
def editar_carga(idcategoria):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        id_materias = request.form.getlist('idmateria')
        cargas_list = request.form.getlist('carga')

        # Eliminar cargas actuales
        cur.execute('DELETE FROM CARGAS WHERE IDCATEGORIA = %s', (idcategoria,))

        # Insertar nuevas materias
        for id_materia, carga_usuario in zip(id_materias, cargas_list):
            try:
                id_materia = int(id_materia)
                carga_usuario_int = int(float(carga_usuario))  # convertir a entero
                carga_base = convertir_carga_a_base(carga_usuario_int)  # unidad base según dígitos
            except ValueError:
                continue

            # Obtener nuevo IDCLAVE
            cur.execute('SELECT MAX(IDCLAVE) AS max_id FROM CARGAS')
            resultado = cur.fetchone()
            idclave = (resultado['max_id'] or 0) + 1

            # Insertar en BD
            cur.execute(
                'INSERT INTO CARGAS(IDCLAVE, IDCATEGORIA, IDMATERIAPRIMA, DESCPORCARGA) VALUES (%s, %s, %s, %s)',
                (idclave, idcategoria, id_materia, carga_base)
            )

        mysql.connection.commit()
        cur.close()
        flash("Carga Actualizada Correctamente", "success")
        return redirect(url_for('cargas'))

    # ===== GET: Mostrar cargas actuales =====
    cur.execute('''
        SELECT 
            c.IDMATERIAPRIMA,
            m.NOMBREMATERIAPRIMA,
            m.CANTIDADUM,
            u.NOMBRE AS UNIDAD,
            c.DESCPORCARGA,
            cat.NOMBRE AS CATEGORIA
        FROM CARGAS c
        JOIN MATERIAPRIMA m ON c.IDMATERIAPRIMA = m.IDMATERIAPRIMA
        JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
        JOIN CATEGORIAPRENDAS cat ON c.IDCATEGORIA = cat.IDCATEGORIA
        WHERE c.IDCATEGORIA = %s
    ''', (idcategoria,))
    cargas_actuales = cur.fetchall()

    # Multiplicar por 1000 si DESCPORCARGA <1 para mostrar legible
    cargas_mostrar = []
    for c in cargas_actuales:
        carga = float(c['DESCPORCARGA'])
        if carga < 1:
            carga_display = int(carga * 1000)
        else:
            carga_display = carga

        # Nombre completo de la materia
        cantidadum = float(c['CANTIDADUM'])
        if c['UNIDAD'].lower() in ['mililitros', 'gramos', 'miligramos']:
            cantidadum_display = int(cantidadum * 1000)
        else:
            cantidadum_display = cantidadum
        nombre_completo = f"{c['NOMBREMATERIAPRIMA']} {cantidadum_display} {c['UNIDAD']}"

        cargas_mostrar.append({
            'IDMATERIAPRIMA': c['IDMATERIAPRIMA'],
            'NOMBRE_COMPLETO': nombre_completo,
            'DESCPORCARGA': carga_display,
            'CATEGORIA': c['CATEGORIA']
        })

    # Materias primas disponibles
    cur.execute('SELECT IDMATERIAPRIMA, NOMBREMATERIAPRIMA FROM MATERIAPRIMA ORDER BY NOMBREMATERIAPRIMA ASC')
    materias = cur.fetchall()
    cur.close()

    return render_template(
        'administrador/cargas/editar_carga.html',
        cargas=cargas_mostrar,
        materias=materias,
        idcategoria=idcategoria
    )

#Eliminar Carga
@app.route('/cargas/eliminar_carga/<int:idcategoria>', methods=['GET'])
def eliminar_carga(idcategoria):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM CARGAS WHERE IDCATEGORIA = %s", (idcategoria,))
    mysql.connection.commit()
    cur.close()
    flash("Carga eliminada correctamente.", "success")
    return redirect(url_for('cargas'))

#Reportes
@app.route('/reportes')
def reportes():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))
    
    return render_template('administrador/reportes/index.html')

# Reportes Ventas
@app.route('/reportesVentas', methods=['GET', 'POST'])
def reportes_ventas():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    ventas = []
    fecha_inicio = None
    fecha_final = None

    if request.method == 'POST':
        fecha_inicio = request.form.get('fechaInicio')
        fecha_final = request.form.get('fechaFinal')

        if not fecha_inicio or not fecha_final:
            flash('⚠️ Por favor seleccione ambas fechas', 'warning')
            return redirect(url_for('reportes_ventas'))
        
        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("""SELECT p.IDPEDIDO,
                                CONCAT(u.NOMBRE, ' ', COALESCE(u.APATERNO, ' ')) AS NOMBRE_CLIENTE,
                                DATE_FORMAT(p.FECHAENTREGA, '%%d/%%m/%%Y') AS FECHAENTREGA,
                                sp.NOMSERVICIO AS SERVICIO,
                                e.NOMESTATUS AS ESTATUS,
                                p.TOTAL,
                                p.PESOTOTAL
                            FROM PEDIDOS p
                            INNER JOIN USUARIO u ON p.IDUSER = u.IDUSER
                            INNER JOIN SERVICIOPEDIDO sp ON p.IDSERVICIO = sp.IDSERVICIO
                            INNER JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
                            WHERE p.FECHAENTREGA BETWEEN %s AND %s AND p.IDESTATUS = 3
                            ORDER BY p.FECHAENTREGA DESC""", (fecha_inicio, fecha_final))
            
            ventas = cur.fetchall()
            cur.close()

            if ventas: 
                flash(f'Se encontraron {len(ventas)} ventas', 'success')
            else:
                flash('No se encontraron ventas en ese rango de fechas', 'warning')

            return render_template('administrador/reportes/reportesVentasResultados.html', ventas=ventas, fecha_inicio=fecha_inicio, fecha_final=fecha_final)

        except Exception as e:
            print(f"❌ Error en /reportesVentas: {e}")
            flash(f'Error al generar el reporte: {str(e)}', 'danger')

    return render_template('administrador/reportes/reportesVentas.html')

# Exportacion PDF Reportes de Ventas
@app.route('/exportar_reporte_ventas', methods=['GET'])
def exportar_reporte_ventas():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    fecha_inicio = request.args.get('fecha_inicio')
    fecha_final = request.args.get('fecha_final')

    if not fecha_inicio or not fecha_final:
        flash('⚠️ Seleccione ambas fechas para generar el reporte de ventas', 'warning')
        return redirect(url_for('reportes_ventas'))

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            SELECT p.IDPEDIDO,
                CONCAT(u.NOMBRE, ' ', COALESCE(u.APATERNO, '')) AS NOMBRE_CLIENTE,
                DATE_FORMAT(p.FECHAENTREGA, '%%d/%%m/%%Y') AS FECHAENTREGA,
                sp.NOMSERVICIO AS SERVICIO,
                e.NOMESTATUS AS ESTATUS,
                p.TOTAL,
                p.PESOTOTAL
            FROM PEDIDOS p
            INNER JOIN USUARIO u ON p.IDUSER = u.IDUSER
            INNER JOIN SERVICIOPEDIDO sp ON p.IDSERVICIO = sp.IDSERVICIO
            INNER JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
            WHERE p.FECHAENTREGA BETWEEN %s AND %s AND p.IDESTATUS = 3
            ORDER BY p.FECHAENTREGA DESC
        """, (fecha_inicio, fecha_final))
        ventas = cur.fetchall()
        cur.close()

        # --- Generar PDF ---
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Cambiar título de PDF
        elements.append(Paragraph("📊 REPORTE DE VENTAS - LAVAEXPRESS", styles["Title"]))
        elements.append(Paragraph(f"Del {fecha_inicio} al {fecha_final}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        if ventas:
            encabezados = ["ID", "Cliente", "Fecha Entrega", "Servicio", "Estatus", "Total ($)", "Peso (kg)"]
            data_tabla = [encabezados]

            total_general = 0
            peso_general = 0
            for t in ventas:
                data_tabla.append([
                    str(t["IDPEDIDO"]),
                    t["NOMBRE_CLIENTE"],
                    t["FECHAENTREGA"],
                    t["SERVICIO"],
                    t["ESTATUS"],
                    f"{float(t['TOTAL']):.2f}",
                    f"{float(t['PESOTOTAL']):.2f}"
                ])
                total_general += float(t["TOTAL"])
                peso_general += float(t["PESOTOTAL"])

            # Totales finales
            data_tabla.append(["", "", "", "", "TOTALES:", f"{total_general:.2f}", f"{peso_general:.2f}"])

            tabla = Table(data_tabla, repeatRows=1)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980b9")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(tabla)
        else:
            elements.append(Paragraph("⚠️ No se encontraron ventas en este rango de fechas.", styles["Normal"]))

        doc.build(elements)
        buffer.seek(0)

        # Cambiar nombre de archivo a ventas
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"reporte_ventas_{fecha_inicio}_a_{fecha_final}.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print("❌ Error al generar PDF:", e)
        flash("Error al generar el reporte PDF de ventas", "danger")
        return redirect(url_for('reportes_ventas'))

#Reportes Reabastecimiento
@app.route('/reportesReabastecimiento')
def reportes_reabastecimiento():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            SELECT
                m.IDMATERIAPRIMA AS ID,
                m.NOMBREMATERIAPRIMA AS NOMBRE,
                CAST(m.CANTIDAD AS DECIMAL(10,2)) AS CANTIDAD,
                CAST(m.STOCKMINIMO AS DECIMAL(10,2)) AS STOCK_MINIMO,
                CAST(m.CANTIDADUM AS DECIMAL(10,2)) AS CANTIDAD_UM,
                u.NOMBRE AS UNIDAD
            FROM MATERIAPRIMA m
            LEFT JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
            ORDER BY m.NOMBREMATERIAPRIMA
        """)
        inventario = cur.fetchall()
        cur.close()

        # Ajustar unidades menores a 1 y formatear números
        for m in inventario:
            # Multiplicar por 1000 si es menor que 1
            if m['CANTIDAD_UM'] < 1:
                m['CANTIDAD_UM'] = float(m['CANTIDAD_UM']) * 1000
            else:
                m['CANTIDAD_UM'] = float(m['CANTIDAD_UM'])

            # Convertir a float para manipular
            m['CANTIDAD'] = float(m['CANTIDAD'])
            m['STOCK_MINIMO'] = float(m['STOCK_MINIMO'])

            # Mostrar enteros si es exacto
            m['CANTIDAD_UM'] = int(m['CANTIDAD_UM']) if m['CANTIDAD_UM'].is_integer() else m['CANTIDAD_UM']
            m['CANTIDAD'] = int(m['CANTIDAD']) if m['CANTIDAD'].is_integer() else m['CANTIDAD']
            m['STOCK_MINIMO'] = int(m['STOCK_MINIMO']) if m['STOCK_MINIMO'].is_integer() else m['STOCK_MINIMO']

        return render_template(
            'administrador/reportes/reportesReabastecimiento.html',
            inventario=inventario
        )

    except Exception as e:
        print(f"❌ Error en /reportesReabastecimiento: {e}")
        flash(f'Error al generar el reporte: {str(e)}', 'danger')
        return render_template('administrador/reportes/reportesReabastecimiento.html', inventario=[])

#Exportacion PDF Reportes de Reabastecimiento
@app.route('/exportar_reporte_reabastecimiento')
def exportar_reporte_reabastecimiento():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            SELECT
                m.IDMATERIAPRIMA AS ID,
                m.NOMBREMATERIAPRIMA AS NOMBRE,
                CAST(m.CANTIDAD AS DECIMAL(10,2)) AS CANTIDAD,
                CAST(m.STOCKMINIMO AS DECIMAL(10,2)) AS STOCK_MINIMO,
                CAST(m.CANTIDADUM AS DECIMAL(10,2)) AS CANTIDAD_UM,
                u.NOMBRE AS UNIDAD
            FROM MATERIAPRIMA m
            INNER JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
            ORDER BY m.NOMBREMATERIAPRIMA
        """)
        inventario = cur.fetchall()
        cur.close()

        if not inventario:
            flash('⚠️ No se encontraron registros para exportar', 'warning')
            return redirect(url_for('reportes_reabastecimiento'))

        for m in inventario:
            if m['CANTIDAD_UM'] < 1:
                m['CANTIDAD_UM'] = float(m['CANTIDAD_UM']) * 1000
            else:
                m['CANTIDAD_UM'] = float(m['CANTIDAD_UM'])

            m['CANTIDAD'] = float(m['CANTIDAD'])
            m['STOCK_MINIMO'] = float(m['STOCK_MINIMO'])

            m['CANTIDAD_UM'] = int(m['CANTIDAD_UM']) if m['CANTIDAD_UM'].is_integer() else m['CANTIDAD_UM']
            m['CANTIDAD'] = int(m['CANTIDAD']) if m['CANTIDAD'].is_integer() else m['CANTIDAD']
            m['STOCK_MINIMO'] = int(m['STOCK_MINIMO']) if m['STOCK_MINIMO'].is_integer() else m['STOCK_MINIMO']

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("📊 REPORTE DE REABASTECIMIENTO - LAVAEXPRESS", styles["Title"]))
        elements.append(Spacer(1, 12))

        data = [["ID", "Materia Prima", "Cantidad (UM)", "Cantidad Existente", "Stock Mínimo"]]
        for m in inventario:
            cantidad_um_str = f"{m['CANTIDAD_UM']} {m['UNIDAD']}"
            data.append([m['ID'], m['NOMBRE'], cantidad_um_str, m['CANTIDAD'], m['STOCK_MINIMO']])

        tabla = Table(data, repeatRows=1)

        estilos = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2980b9")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ]

        for i, m in enumerate(inventario):
            if m['CANTIDAD'] < m['STOCK_MINIMO']:
                estilos.append(('BACKGROUND', (0, i+1), (-1, i+1), colors.HexColor("#f8d7da")))

        tabla.setStyle(TableStyle(estilos))
        elements.append(tabla)
        elements.append(Spacer(1,12))

        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="reporte_reabastecimiento.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print(f"❌ Error al generar PDF de reabastecimiento: {e}")
        flash("Error al generar el PDF de reabastecimiento", "danger")
        return redirect(url_for('reportes_reabastecimiento'))

# Reportes Inventario
@app.route('/reportesInventario')
def reportes_inventario():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            SELECT
                m.IDMATERIAPRIMA AS ID,
                m.NOMBREMATERIAPRIMA AS NOMBRE,
                CAST(m.CANTIDAD AS DECIMAL(10,2)) AS CANTIDAD,
                CAST(m.STOCKMINIMO AS DECIMAL(10,2)) AS STOCK_MINIMO,
                CAST(m.CANTIDADUM AS DECIMAL(10,2)) AS CANTIDAD_UM,
                u.NOMBRE AS UNIDAD
            FROM MATERIAPRIMA m
            LEFT JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
            ORDER BY m.NOMBREMATERIAPRIMA
        """)
        inventario = cur.fetchall()
        cur.close()

        # Ajustar unidades menores a 1 y formatear números
        for m in inventario:
            if m['CANTIDAD_UM'] < 1:
                m['CANTIDAD_UM'] = float(m['CANTIDAD_UM']) * 1000
            else:
                m['CANTIDAD_UM'] = float(m['CANTIDAD_UM'])

            m['CANTIDAD'] = float(m['CANTIDAD'])
            m['STOCK_MINIMO'] = float(m['STOCK_MINIMO'])

            m['CANTIDAD_UM'] = int(m['CANTIDAD_UM']) if m['CANTIDAD_UM'].is_integer() else m['CANTIDAD_UM']
            m['CANTIDAD'] = int(m['CANTIDAD']) if m['CANTIDAD'].is_integer() else m['CANTIDAD']
            m['STOCK_MINIMO'] = int(m['STOCK_MINIMO']) if m['STOCK_MINIMO'].is_integer() else m['STOCK_MINIMO']

        return render_template(
            'administrador/reportes/reportesInventario.html',
            inventario=inventario
        )

    except Exception as e:
        print(f"❌ Error en /reportesInventario: {e}")
        flash(f'Error al generar el reporte: {str(e)}', 'danger')
        return render_template('administrador/reportes/reportesInventario.html', inventario=[])

# Exportacion PDF Reportes de Inventario
@app.route('/exportar_reporte_inventario')
def exportar_reporte_inventario():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            SELECT
                m.IDMATERIAPRIMA AS ID,
                m.NOMBREMATERIAPRIMA AS NOMBRE,
                CAST(m.CANTIDAD AS DECIMAL(10,2)) AS CANTIDAD,
                CAST(m.STOCKMINIMO AS DECIMAL(10,2)) AS STOCK_MINIMO,
                CAST(m.CANTIDADUM AS DECIMAL(10,2)) AS CANTIDAD_UM,
                u.NOMBRE AS UNIDAD
            FROM MATERIAPRIMA m
            LEFT JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
            ORDER BY m.NOMBREMATERIAPRIMA
        """)
        inventario = cur.fetchall()
        cur.close()

        if not inventario:
            flash('⚠️ No se encontraron registros para exportar', 'warning')
            return redirect(url_for('reportes_inventario'))

        # Ajustar unidades y números
        for m in inventario:
            if m['CANTIDAD_UM'] < 1:
                m['CANTIDAD_UM'] = float(m['CANTIDAD_UM']) * 1000
            else:
                m['CANTIDAD_UM'] = float(m['CANTIDAD_UM'])

            m['CANTIDAD'] = float(m['CANTIDAD'])
            m['STOCK_MINIMO'] = float(m['STOCK_MINIMO'])

            m['CANTIDAD_UM'] = int(m['CANTIDAD_UM']) if m['CANTIDAD_UM'].is_integer() else m['CANTIDAD_UM']
            m['CANTIDAD'] = int(m['CANTIDAD']) if m['CANTIDAD'].is_integer() else m['CANTIDAD']
            m['STOCK_MINIMO'] = int(m['STOCK_MINIMO']) if m['STOCK_MINIMO'].is_integer() else m['STOCK_MINIMO']

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("📊 REPORTE DE INVENTARIO - LAVAEXPRESS", styles["Title"]))
        elements.append(Spacer(1, 12))

        data = [["ID", "Materia Prima", "Cantidad (UM)", "Cantidad Existente", "Stock Mínimo"]]
        for m in inventario:
            cantidad_um_str = f"{m['CANTIDAD_UM']} {m['UNIDAD']}"
            data.append([m['ID'], m['NOMBRE'], cantidad_um_str, m['CANTIDAD'], m['STOCK_MINIMO']])

        tabla = Table(data, repeatRows=1)

        estilos = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2980b9")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ]



        tabla.setStyle(TableStyle(estilos))
        elements.append(tabla)
        elements.append(Spacer(1,12))

        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="reporte_inventario.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print(f"❌ Error al generar PDF de inventario: {e}")
        flash("Error al generar el PDF de inventario", "danger")
        return redirect(url_for('reportes_inventario'))

#Reportes Tickets
@app.route('/reportesTicket', methods=['GET', 'POST'])
def reportes_tickets():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST':
        fecha_inicio = request.form.get('fechaInicio')
        fecha_final = request.form.get('fechaFinal')

        if not fecha_inicio or not fecha_final:
            flash('⚠️ Por favor seleccione ambas fechas', 'warning')
            return redirect(url_for('reportes_tickets'))

        pedidos_detalles = []

        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Traer tickets
            cur.execute("""
                SELECT p.IDPEDIDO,
                    CONCAT(u.NOMBRE, ' ', COALESCE(u.APATERNO, '')) AS CLIENTE,
                    p.FECHAENTREGA,
                    sp.NOMSERVICIO AS SERVICIO,
                    e.NOMESTATUS AS ESTATUS,
                    p.TOTAL,
                    p.PESOTOTAL,
                    p.IDSERVICIO
                FROM PEDIDOS p
                INNER JOIN USUARIO u ON p.IDUSER = u.IDUSER
                INNER JOIN SERVICIOPEDIDO sp ON p.IDSERVICIO = sp.IDSERVICIO
                INNER JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
                WHERE p.FECHAENTREGA BETWEEN %s AND %s
                ORDER BY p.FECHAENTREGA DESC
            """, (fecha_inicio, fecha_final))
            tickets = cur.fetchall()

            # Para cada ticket, traer prendas
            for t in tickets:
                cur.execute("""
                    SELECT cat.NOMBRE AS categoria,
                        d.CANTIDAD AS cantidad,
                        d.PESO AS peso,
                        cat.PRECIOKG AS precio_x_kg
                    FROM PEDIDOS_HAS_CATALOGODETALLE d
                    INNER JOIN CATEGORIAPRENDAS cat ON d.IDCATALOGO = cat.IDCATEGORIA
                    WHERE d.IDPEDIDO = %s
                    ORDER BY cat.NOMBRE
                """, (t['IDPEDIDO'],))
                prendas = cur.fetchall()

                total_peso = sum(float(p['peso']) for p in prendas)
                total_costo = sum(float(p['peso']) * float(p['precio_x_kg']) for p in prendas)

                # Costo por servicio
                cur.execute("SELECT COSTO_KG FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s", (t['IDSERVICIO'],))
                servicio = cur.fetchone()
                if servicio:
                    total_costo += total_peso * float(servicio['COSTO_KG'])

                pedidos_detalles.append({
                    'pedido': t,
                    'prendas': prendas,
                    'total_peso': total_peso,
                    'total_costo': total_costo
                })

            cur.close()

        except Exception as e:
            print(f"❌ Error en /reportesTicket: {e}")
            flash(f'Error al generar el reporte: {str(e)}', 'danger')

        return render_template(
            'administrador/reportes/reportesTicketResultados.html',
            pedidos_detalles=pedidos_detalles,
            fecha_inicio=fecha_inicio,
            fecha_final=fecha_final
        )

    # GET: mostrar solo formulario
    return render_template('administrador/reportes/reportesTicket.html')

# Exportacion PDF Reportes
@app.route('/exportar_reporte_tickets', methods=['GET'])
def exportar_reporte_tickets():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    fecha_inicio = request.args.get('fecha_inicio')
    fecha_final = request.args.get('fecha_final')

    if not fecha_inicio or not fecha_final:
        flash('⚠️ Seleccione ambas fechas para generar el reporte', 'warning')
        return redirect(url_for('reportes_tickets'))

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Traer tickets dentro del rango
        cur.execute("""
            SELECT p.IDPEDIDO,
                CONCAT(u.NOMBRE, ' ', COALESCE(u.APATERNO, '')) AS CLIENTE,
                p.FECHAENTREGA,
                sp.NOMSERVICIO AS SERVICIO,
                e.NOMESTATUS AS ESTATUS,
                p.TOTAL,
                p.PESOTOTAL,
                p.IDSERVICIO
            FROM PEDIDOS p
            INNER JOIN USUARIO u ON p.IDUSER = u.IDUSER
            INNER JOIN SERVICIOPEDIDO sp ON p.IDSERVICIO = sp.IDSERVICIO
            INNER JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
            WHERE p.FECHAENTREGA BETWEEN %s AND %s
            ORDER BY p.FECHAENTREGA DESC
        """, (fecha_inicio, fecha_final))
        tickets = cur.fetchall()

        if not tickets:
            flash('⚠️ No se encontraron tickets en ese rango de fechas', 'warning')
            return redirect(url_for('reportes_tickets'))

        # --- Crear PDF ---
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("📊 REPORTE DETALLADO DE TICKETS - LAVAEXPRESS", styles["Title"]))
        elements.append(Paragraph(f"Del {fecha_inicio} al {fecha_final}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Iterar tickets
        for t in tickets:
            elements.append(Paragraph(f"🧾 Ticket #{t['IDPEDIDO']} - Cliente: {t['CLIENTE']}", styles["Heading2"]))
            elements.append(Paragraph(f"Fecha Entrega: {t['FECHAENTREGA']} | Estatus: {t['ESTATUS']} | Servicio: {t['SERVICIO']}", styles["Normal"]))
            elements.append(Spacer(1, 6))

            # Detalles de prendas
            cur.execute("""
                SELECT cat.NOMBRE AS categoria, c.NOMBREPRENDA AS prenda, d.CANTIDAD AS cantidad,
                    d.PESO AS peso, cat.PRECIOKG AS precio_x_kg
                FROM PEDIDOS_HAS_CATALOGODETALLE d
                INNER JOIN CATALOGOPRENDAS c ON d.IDCATALOGO = c.IDCATALOGO
                INNER JOIN CATEGORIAPRENDAS cat ON c.IDCATEGORIA = cat.IDCATEGORIA
                WHERE d.IDPEDIDO = %s
                ORDER BY cat.NOMBRE, c.NOMBREPRENDA
            """, (t['IDPEDIDO'],))
            prendas = cur.fetchall()

            total_cantidad = sum(float(p['cantidad']) for p in prendas)
            total_peso = sum(float(p['peso']) for p in prendas)
            total_costo = sum(float(p['peso']) * float(p['precio_x_kg']) for p in prendas)

            # Costo por servicio
            cur.execute("SELECT COSTO_KG FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s", (t['IDSERVICIO'],))
            servicio = cur.fetchone()
            if servicio:
                total_costo += total_peso * float(servicio['COSTO_KG'])

            if prendas:
                data_tabla = [["Categoría", "Prenda", "Cantidad", "Peso (kg)", "Precio x kg"]]
                for p in prendas:
                    data_tabla.append([
                        p['categoria'],
                        p['prenda'],
                        f"{float(p['cantidad']):.2f}",
                        f"{float(p['peso']):.2f}",
                        f"${float(p['precio_x_kg']):.2f}"
                    ])
                data_tabla.append(["", "TOTALES:", f"{total_cantidad:.2f}", f"{total_peso:.2f}", f"${total_costo:.2f}"])

                tabla = Table(data_tabla, repeatRows=1)
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980b9")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(tabla)
                elements.append(Spacer(1, 12))
            else:
                elements.append(Paragraph("⚠️ No se encontraron prendas para este ticket.", styles["Normal"]))
                elements.append(Spacer(1, 12))

        cur.close()
        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"reporte_detalle_tickets_{fecha_inicio}_a_{fecha_final}.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print(f"❌ Error al generar PDF detallado de tickets: {e}")
        flash("Error al generar el reporte PDF detallado", "danger")
        return redirect(url_for('reportes_tickets'))

#Roles
@app.route('/roles', methods=['GET', 'POST'])
def roles():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST' and 'nombre' in request.form:
        
        #Capturamos el nuevo rol
        nombre = request.form['nombre']

        #Creamos nuevo cursor de bd. objeto que permitirá realizar CRUD en la BD
        cur = mysql.connection.cursor()

        #Obtener el ultimo ID de USUARIO

        cur.execute('SELECT MAX(IDROL) AS max_id FROM ROLES') 
        #AS max_id es una variable temporal que guardará los datos obtenidos en MAX(USER)

        result = cur.fetchone()
        #Recupera el resultado de la consulta

        id = (result['max_id'] or 0) + 1 
        #En result accedemos al valor obtenido en max_id, el "or 0" da entender que en caso de que sea NULO le asigne valor 0.

        #Generamos INSERT
        cur.execute('INSERT INTO ROLES (IDROL, NOMROL) VALUES (%s,%s)', (id,nombre))

        #Hacemos commit al INSERT para que se guarde en la BD
        mysql.connection.commit()

        #Cerramos el cursor de la BD como buena practica.
        cur.close()

        #Mandamos mensaje de exito
        flash("✅ Nuevo rol creado con éxito", "success")
        
        #Actualizamos la página de roles
        return redirect(url_for('roles'))
    
    #Si solo quiere observar la página con GET, se debe de mostrar los roles existentes
    #Aquí también existira una consulta a la BD
    cur = mysql.connection.cursor()

    cur.execute('SELECT IDROL, NOMROL FROM ROLES')
    roles = cur.fetchall() #Se usa fetchall porque son N datos. Este es la 2da variable del return
    cur.close()

    #ROLES = ROLES
    #El primer "roles" será la variable que estará disponible en el HTML aplicando Jinja2
    #El segundo "roles" es la variable con valores obtenidos de la BD
    return render_template('administrador/roles/roles.html', roles = roles)

#Editar Rol
@app.route('/roles/editar/<int:idrol>', methods=['GET', 'POST'])
def editar_rol(idrol):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST':
        #Capturamos los datos del formulario
        nombre = request.form['nombre']

        #Creamos instancia de BD
        cur = mysql.connection.cursor()

        #Generamos un UPDATE
        cur.execute('UPDATE ROLES SET NOMROL=%s WHERE IDROL=%s', (nombre, idrol))

        #Guardamos UPDATE
        mysql.connection.commit()

        #Cerramos instancia BD
        cur.close()

        #Mensaje de exito
        flash("✅ Dato actualizado correctamente", "success")
        return redirect(url_for('roles'))
    
    #Si es GET, mostrar los datos actuales
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM ROLES WHERE IDROL=%s', (idrol,))
    rol = cur.fetchone()
    cur.close()

    return render_template('administrador/roles/editarRol.html', rol=rol)

#Eliminar Rol
@app.route('/roles/eliminar/<int:idrol>')
def eliminar_rol(idrol):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM ROLES WHERE IDROL=%s', (idrol,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Rol eliminado correctamente", "success")
    return redirect(url_for('roles'))

# ===== Conversión de cantidad a unidad base según dígitos =====
def convertir_a_unidad_base(cantidad):
    cantidad_str = str(cantidad).strip()
    if len(cantidad_str) == 3:
        # 3 dígitos → mililitros o gramos → dividir entre 1000
        cantidad_base = float(cantidad_str) / 1000
    elif len(cantidad_str) == 1:
        # 1 dígito → litros o kilogramos → mantener igual
        cantidad_base = float(cantidad_str)
    else:
        raise ValueError("Solo se permiten cantidades de 1 o 3 dígitos")
    return cantidad_base

# NUEVA MATERIA PRIMA
@app.route('/materiaPrima', methods=['GET', 'POST'])
def materiaPrima():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST' and 'nombre' in request.form and 'stock' in request.form and 'unidad' in request.form and 'cantidadum' in request.form:

        # Capturamos los datos ingresados en el form
        nombre = request.form['nombre'].strip()
        stock = request.form['stock'].strip()
        unidad = request.form['unidad'].strip()
        cantidadinput = request.form['cantidadum'].strip()

        try:
            # Convertimos a unidad base usando solo dígitos 1 o 3
            cantidadum = convertir_a_unidad_base(cantidadinput)
        except ValueError as e:
            flash(f"❌ {e}", "danger")
            return redirect(url_for('materiaPrima'))

        # Creamos una instancia de BD
        cur = mysql.connection.cursor()

        # Verificar si ya existe la materia prima
        cur.execute(
            'SELECT * FROM MATERIAPRIMA WHERE LOWER(NOMBREMATERIAPRIMA) = %s AND IDUNIDAD = %s AND CANTIDADUM = %s',
            (nombre.lower(), unidad, cantidadum)
        )
        existente = cur.fetchone()

        if existente:
            flash("❌ La materia prima con esa unidad y cantidad ya existe", "danger")
            cur.close()
            return redirect(url_for('materiaPrima'))

        # Obtener el último ID
        cur.execute('SELECT MAX(IDMATERIAPRIMA) AS max_id FROM MATERIAPRIMA')
        result = cur.fetchone()
        id = (result['max_id'] or 0) + 1

        # Generar INSERT
        cur.execute(
            'INSERT INTO MATERIAPRIMA(IDMATERIAPRIMA, NOMBREMATERIAPRIMA, CANTIDAD, STOCKMINIMO, IDUNIDAD, CANTIDADUM) VALUES (%s, %s, %s, %s, %s, %s)',
            (id, nombre, 0, stock, unidad, cantidadum)
        )

        # Guardar INSERT
        mysql.connection.commit()
        cur.close()

        flash("✅ Materia Prima creada de manera exitosa", "success")
        return redirect(url_for('materiaPrima'))

    # SI ES GET: mostrar materias primas existentes
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT mp.IDMATERIAPRIMA, mp.NOMBREMATERIAPRIMA, mp.CANTIDAD, mp.CANTIDADUM, mp.IDUNIDAD, u.NOMBRE AS UNIDAD
        FROM MATERIAPRIMA mp
        JOIN UNIDADESMEDIDA u ON mp.IDUNIDAD = u.IDUNIDAD
        ORDER BY mp.NOMBREMATERIAPRIMA
    ''')
    materias = cur.fetchall()

    # Convertir de unidad base a mostrar (simplemente multiplicar si quieres revertir)
    # Solo manejamos 1 dígito (L o kg) y 3 dígitos (ml o g)
    for m in materias:
        cantidad_base = float(m['CANTIDADUM'])
        if int(m['IDUNIDAD']) in [3, 4, 5]:  # unidades pequeñas que se ingresan con 3 dígitos
            m['CANTIDADUM_MOSTRAR'] = cantidad_base * 1000
        else:  # unidades grandes que se ingresan con 1 dígito
            m['CANTIDADUM_MOSTRAR'] = cantidad_base

    # Obtener unidades disponibles para el select
    cur.execute('SELECT IDUNIDAD, NOMBRE FROM UNIDADESMEDIDA')
    unidadess = cur.fetchall()
    cur.close()

    return render_template('administrador/materiaPrima/materiaPrima.html', materias=materias, unidadess=unidadess)

#Editar Materia Prima
# ===== Editar Materia Prima =====
@app.route('/materiaPrima/editar_materia/<int:idmateriaprima>', methods=['GET', 'POST'])
def editar_materia(idmateriaprima):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        # Capturamos los datos del formulario
        nombre = request.form['nombre'].strip()
        cantidad = request.form['cantidad'].strip()
        stock = request.form['stock'].strip()
        unidad = request.form['unidad'].strip()
        cantidadum_input = request.form['cantidadum'].strip()  # valor ingresado en el form

        # ===== CONVERTIR CANTIDAD DE UNIDAD A BASE =====
        try:
            cantidadum = convertir_a_unidad_base(cantidadum_input)
        except ValueError as e:
            flash(f"❌ {e}", "danger")
            return redirect(url_for('editar_materia', idmateriaprima=idmateriaprima))

        # Actualizar la materia prima
        cur.execute('''
            UPDATE MATERIAPRIMA 
            SET NOMBREMATERIAPRIMA = %s, CANTIDAD = %s, STOCKMINIMO = %s, IDUNIDAD = %s, CANTIDADUM = %s
            WHERE IDMATERIAPRIMA = %s
        ''', (nombre, cantidad, stock, unidad, cantidadum, idmateriaprima))

        mysql.connection.commit()
        cur.close()

        flash("✅ Dato actualizado correctamente", "success")
        return redirect(url_for('materiaPrima'))

    # ===== GET: mostrar datos actuales =====
    cur.execute('''
        SELECT mp.IDMATERIAPRIMA, mp.NOMBREMATERIAPRIMA, mp.CANTIDAD, mp.STOCKMINIMO, mp.CANTIDADUM, u.IDUNIDAD, u.NOMBRE AS UNIDAD
        FROM MATERIAPRIMA mp 
        JOIN UNIDADESMEDIDA u ON mp.IDUNIDAD = u.IDUNIDAD 
        WHERE mp.IDMATERIAPRIMA = %s
    ''', (idmateriaprima,))
    materia = cur.fetchone()

    if not materia:
        flash("❌ Materia prima no encontrada", "danger")
        cur.close()
        return redirect(url_for('materiaPrima'))

    # ===== Convertir de unidad base a mostrar =====
    if int(materia['IDUNIDAD']) in [3, 4, 5]:  # unidades pequeñas (ml, g, mg)
        cantidadum_mostrar = float(materia['CANTIDADUM']) * 1000
    else:  # unidades grandes (L, kg)
        cantidadum_mostrar = float(materia['CANTIDADUM'])

    # Ajuste singular/plural de la unidad
    unidad_nombre = materia['UNIDAD']
    if cantidadum_mostrar == 1 and unidad_nombre.endswith('s'):
        unidad_nombre = unidad_nombre[:-1]

    materia['CANTIDADUM_MOSTRAR'] = cantidadum_mostrar
    materia['UNIDAD_MOSTRAR'] = unidad_nombre

    # Obtener unidades disponibles
    cur.execute('SELECT IDUNIDAD, NOMBRE FROM UNIDADESMEDIDA')
    unidades = cur.fetchall()
    cur.close()

    return render_template(
        'administrador/materiaPrima/editarMateriaPrima.html',
        materia=materia,
        unidades=unidades
    )

#Eliminar MateriaPrima
@app.route('/materiaPrima/eliminar_materia/<int:idmateriaprima>',methods=['GET'])
def eliminar_materia(idmateriaprima):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    #Creamos instancia BD
    cur = mysql.connection.cursor()

    #Ejecutamos DELETE
    cur.execute('DELETE FROM MATERIAPRIMA WHERE IDMATERIAPRIMA=%s',(idmateriaprima,))

    #Guardamos sentencia en la bd
    mysql.connection.commit()
    
    #Cerramos BD
    cur.close()

    #Mensaje Exito
    flash("✅ Materia Prima eliminada correctamente", "success")
    return redirect(url_for('materiaPrima'))

#Nuevo servicio
@app.route('/servicios', methods=['GET', 'POST'])
def servicios():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST' and 'nombre' in request.form:
        #Capturamos los datos
        nombre = request.form['nombre']
        costo_kg = float(request.form['costo_kg'])

        #Creamos instancia BD
        cur =mysql.connection.cursor()

        #Verificamos que no exista datos duplicados
        cur.execute('SELECT * FROM SERVICIOPEDIDO WHERE LOWER(NOMSERVICIO) = %s', (nombre.lower(),))
        existente = cur.fetchone()

        if existente:
            flash("❌ El tipo de servicio ya existe", "danger")
            return redirect(url_for('servicios'))
        
        #Obtener el ultimo id
        cur.execute('SELECT MAX(IDSERVICIO) AS max_id FROM SERVICIOPEDIDO')
        result = cur.fetchone()
        id = (result['max_id'] or 0) + 1
        
        #Si no existe, generamos INSERT
        cur.execute('INSERT INTO SERVICIOPEDIDO (IDSERVICIO, NOMSERVICIO, COSTO_KG) VALUES (%s, %s, %s)', (id, nombre, costo_kg),)

        #Guardamos INSERT
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Tipo de servicio creado de manera éxitosa", "success")
        return redirect(url_for('servicios'))
    
    # Si el metodo es GET, mostramos los datos existentes
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDSERVICIO, NOMSERVICIO, COSTO_KG FROM SERVICIOPEDIDO')
    servicios = cur.fetchall()

    return render_template('/administrador/servicios/servicios.html', servicios = servicios)

#Editar Servicios
@app.route('/servicios/editar_servicios/<int:idservicio>', methods=['GET', 'POST'])
def editar_servicios(idservicio):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST':
        #Recuperar nuevos datos
        nombre = request.form['nombre']
        costo_kg = float(request.form['costo_kg'])

        #Crear instancia BD
        cur = mysql.connection.cursor()

        #Generar UPDATE
        cur.execute('UPDATE SERVICIOPEDIDO SET NOMSERVICIO = %s, COSTO_KG = %s WHERE IDSERVICIO = %s', (nombre, costo_kg, idservicio))

        #Guardar UPDATE
        mysql.connection.commit()

        #Cerrar BD
        cur.close()

        #Mensaje éxito
        flash("✅ Dato actualizado correctamente", "success")
        return redirect(url_for('servicios'))
    
    #Si es GET, MUESTRA LOS DATOS A EDITAR
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDSERVICIO, NOMSERVICIO, COSTO_KG FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s', (idservicio,))
    servicio = cur.fetchone()
    cur.close()
    return render_template('administrador/servicios/editarServicios.html', servicio = servicio)

#Eliminar Servicios
@app.route('/servicios/eliminar_servicios/<int:idservicio>')
def eliminar_servicios(idservicio):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s', (idservicio,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Tipo de servicio eliminado correctamente", "success")
    return redirect(url_for('servicios'))

#Nuevo Estatus
@app.route('/estatus', methods=['GET', 'POST'])
def estatus():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))
    
    if request.method == 'POST':
        #Capturamos los datos del form
        nombre = request.form['nombre']

        #Creamos instancia de la BD
        cur = mysql.connection.cursor()

        #Verificamos que no exista datos duplicados
        cur.execute('SELECT * FROM ESTATUSPEDIDO WHERE LOWER(NOMESTATUS) = %s', (nombre.lower(),))
        existente = cur.fetchone()

        #Si existe mandamos mensaje de error
        if existente:
            flash("❌ El estatus ya existe", "danger")
            return redirect(url_for('estatus'))
        
        #Obtener el ultimo ID
        cur.execute('SELECT MAX(IDESTATUS) AS max_id FROM ESTATUSPEDIDO')
        resultado = cur.fetchone()
        id = (resultado['max_id'] or 0) + 1
        
        #Si no existe, procedemos con el INSERT
        cur.execute('INSERT INTO ESTATUSPEDIDO(IDESTATUS, NOMESTATUS) VALUES (%s, %s)', (id, nombre),)

        #Hacemos COMMIT
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de exito
        flash("✅ Tipo de estatus creado de manera éxitosa", "success")

        return redirect(url_for('estatus'))
    #Si es GET, mostrar los datos Existentes
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDESTATUS, NOMESTATUS FROM ESTATUSPEDIDO')
    estatus = cur.fetchall()

    return render_template('administrador/estatus/estatus.html', estatus = estatus)

#Editar Estatus
@app.route('/estatus/editar_estatus/<int:idestatus>', methods=['GET', 'POST'])
def editar_estatus(idestatus):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST':
        #Capturamos los nuevos valores
        nombre = request.form['nombre']

        #Creamos una instancia de BD
        cur = mysql.connection.cursor()

        #Ejecutamos UPDATE
        cur.execute('UPDATE ESTATUSPEDIDO SET NOMESTATUS = %s WHERE IDESTATUS = %s',(nombre,idestatus))

        #Guardamos UPDATE
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de exito
        flash("✅ Dato actualizado correctamente", "success")

        return redirect(url_for('estatus'))
    
    #Si es GET mostramos los datos a editar
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDESTATUS, NOMESTATUS FROM ESTATUSPEDIDO WHERE IDESTATUS = %s', (idestatus,))
    estatu = cur.fetchone()
    cur.close()
    return render_template('administrador/estatus/editarEstatus.html', estatu = estatu)

#Eliminar Estatus
@app.route('/estatus/eliminar_estatus/<int:idestatus>')
def eliminar_estatus(idestatus):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM ESTATUSPEDIDO WHERE IDESTATUS = %s', (idestatus,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Tipo de estatus eliminado correctamente", "success")

    return redirect(url_for('estatus'))

#Nueva Unidad de Medida
@app.route('/unidadesMedidas', methods=['GET', 'POST'])
def unidadesMedidas():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST' and 'nombre' in request.form:
        #Capturamos los datos del FORM
        nombre = request.form['nombre']

        #Creamos instancia BD
        cur = mysql.connection.cursor()

        #Verificamos que no exista datos duplicados
        cur.execute('SELECT * FROM UNIDADESMEDIDA WHERE LOWER(NOMBRE) = %s', (nombre.lower(),))
        existente = cur.fetchone()

        #Si ya existe
        if existente:
            #Mensaje de duplicidad
            flash("❌ La unidad de medida ya existe", "danger")
            cur.close()
            return redirect(url_for('unidadesMedidas'))
        
        #Obtenemos el ultimo ID
        cur.execute('SELECT MAX(IDUNIDAD) AS max_id FROM UNIDADESMEDIDA')
        resultado = cur.fetchone()
        id = (resultado['max_id'] or 0) + 1

        #Generamos INSERT
        cur.execute('INSERT INTO UNIDADESMEDIDA(IDUNIDAD, NOMBRE) VALUES (%s, %s)', (id, nombre),)

        #Guardamos INSERT
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Unidad de medida creado de manera éxitosa", "success")
        
        return redirect(url_for('unidadesMedidas'))
    
    #Si es GET, mostrar datos existentes
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDUNIDAD, NOMBRE FROM UNIDADESMEDIDA')
    unidades = cur.fetchall()
    return render_template('administrador/unidadesMedida/unidadesMedida.html', unidades = unidades)

#Editar Unidad de Medida
@app.route('/unidadesMedidas/editar_unidad/<int:idunidad>', methods=['GET', 'POST'])
def editar_unidad(idunidad):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    if request.method == 'POST':
        #Capturar los datos del FORM
        nombre = request.form['nombre']

        #Creamos instancia BD
        cur = mysql.connection.cursor()

        #Generamos UPDATE
        cur.execute('UPDATE UNIDADESMEDIDA SET NOMBRE = %s WHERE IDUNIDAD = %s', (nombre, idunidad))

        #Guardamos UPDATE
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de exito
        flash("✅ Dato actualizado correctamente", "success")
        return redirect(url_for('unidadesMedidas'))
    
    #Si es GET, mostrar los datos a editar
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDUNIDAD, NOMBRE FROM UNIDADESMEDIDA WHERE IDUNIDAD = %s', (idunidad,))
    unidad = cur.fetchone()
    cur.close()
    return render_template('administrador/unidadesMedida/editarUnidad.html', unidad = unidad)

#Eliminar Medida de Unidad
@app.route('/unidadesMedidas/eliminar_unidad/<int:idunidad>')
def eliminar_unidad(idunidad):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM UNIDADESMEDIDA WHERE IDUNIDAD = %s', (idunidad,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Unidad de medida eliminado correctamente", "success")

    return redirect(url_for('unidadesMedidas'))

#Función Loggout HTML
@app.route('/loggoutAdmin')
def loggout():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))
    return render_template('administrador/loggoutAdmin.html')

#Función Loggout
@app.route('/cerrar_sesion')
def cerrar_sesion():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 1:
        return redirect(url_for('cerrar_sesion_restringidas'))

    session.clear()
    flash("✅ Sesión cerrada correctamente", "success")
    return redirect(url_for('index'))





#Cliente
#Función Mis Pedidos
@app.route('/misPedidos')
def misPedidos():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol cliente
    if session.get('rol') != 2:
        return redirect(url_for('cerrar_sesion_restringidas'))

    user_id = session.get('id')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT p.IDPEDIDO, p.FECHAENTREGA, e.NOMESTATUS
        FROM PEDIDOS p
        JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
        WHERE p.IDUSER = %s
        ORDER BY p.IDPEDIDO DESC
    """, (user_id,))
    pedidos = cur.fetchall()
    cur.close()
    return render_template('cliente/misPedidos.html', pedidos=pedidos)

# Detalles Pedido (Cliente)
@app.route('/detalle_pedido/<int:idpedido>')
def detalle_pedido(idpedido):
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 2:
        return redirect(url_for('cerrar_sesion_restringidas'))

    try:
        # Verifica sesión activa
        if not session.get('logueado'):
            return jsonify({"success": False, "message": "No autorizado"}), 401

        user_id = session['id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Info general del pedido (solo si pertenece al usuario logueado)
        cur.execute("""
            SELECT p.IDPEDIDO, p.FECHAENTREGA, p.IDSERVICIO, e.NOMESTATUS AS ESTATUS,
                s.NOMSERVICIO, CONCAT(u.NOMBRE,' ',u.APATERNO) AS CLIENTE
            FROM PEDIDOS p
            INNER JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
            INNER JOIN SERVICIOPEDIDO s ON p.IDSERVICIO = s.IDSERVICIO
            INNER JOIN USUARIO u ON p.IDUSER = u.IDUSER
            WHERE p.IDPEDIDO = %s AND p.IDUSER = %s
        """, (idpedido, user_id))
        pedido = cur.fetchone()
        if not pedido:
            return jsonify({"success": False, "message": "Pedido no encontrado"}), 404

        # Detalle de prendas (idéntico al de /pedidos/detalles)
        cur.execute("""
            SELECT c.NOMBREPRENDA AS nombre, d.CANTIDAD AS cantidad, 
                d.PESO AS peso, cat.PRECIOKG AS precio_x_kg
            FROM PEDIDOS_HAS_CATALOGODETALLE d
            INNER JOIN CATALOGOPRENDAS c ON d.IDCATALOGO = c.IDCATALOGO
            INNER JOIN CATEGORIAPRENDAS cat ON c.IDCATEGORIA = cat.IDCATEGORIA
            WHERE d.IDPEDIDO = %s
        """, (idpedido,))
        prendas = cur.fetchall()

        # Totales
        total_peso = sum(float(p['peso']) for p in prendas)
        total_costo = sum(float(p['peso']) * float(p['precio_x_kg']) for p in prendas)

        # Costo adicional del servicio
        cur.execute("SELECT COSTO_KG FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s", (pedido['IDSERVICIO'],))
        servicio = cur.fetchone()
        if servicio:
            total_costo += total_peso * float(servicio['COSTO_KG'])

        cur.close()

        # Mismo formato JSON que la ruta original
        return jsonify({
            "success": True,
            "idpedido": pedido['IDPEDIDO'],
            "cliente": pedido['CLIENTE'],
            "fecha_entrega": str(pedido['FECHAENTREGA']),
            "estatus": pedido['ESTATUS'],
            "servicio": pedido['NOMSERVICIO'],
            "prendas": prendas,
            "peso_total": total_peso,
            "costo_total": total_costo
        })

    except Exception as e:
        print(f"❌ Error en /detalle_pedido/{idpedido}: {e}")
        return jsonify({
            "success": False,
            "message": "Error al obtener detalles del pedido",
            "error": str(e)
        }), 500

#Buscar por ID o Fecha
@app.route('/buscar_mispedidos')
def buscar_mispedidos():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 2:
        return redirect(url_for('cerrar_sesion_restringidas'))

    termino = request.args.get('q', '')
    user_id = session['id']
    cur = mysql.connection.cursor()
    query = """
        SELECT p.IDPEDIDO, p.FECHAENTREGA, e.NOMESTATUS
        FROM PEDIDOS p
        JOIN ESTATUSPEDIDO e ON p.IDESTATUS = e.IDESTATUS
        WHERE p.IDUSER = %s AND (p.IDPEDIDO LIKE %s OR p.FECHAENTREGA LIKE %s)
        ORDER BY p.IDPEDIDO DESC
    """
    like_term = f"%{termino}%"
    cur.execute(query, (user_id, like_term, like_term))
    resultados = cur.fetchall()
    cur.close()
    return jsonify([dict(zip([key[0] for key in cur.description], row)) for row in resultados])

#Función Actualizar Datos
@app.route('/actualizarDatos', methods=['GET', 'POST'])
def actualizarDatos():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 2:
        return redirect(url_for('cerrar_sesion_restringidas'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')

        cur.execute(
            'UPDATE USUARIO SET NOMBRE=%s, APATERNO=%s, CORREO=%s WHERE IDUSER=%s',
            (nombre, apellido, correo, iduser)
        )
        mysql.connection.commit()
        cur.close()

        flash("✅ Datos actualizados correctamente", "success")
        return redirect(url_for('misPedidos'))

    # Mostrar datos actuales
    cur.execute('SELECT IDUSER, NOMBRE, APATERNO, CORREO FROM USUARIO WHERE IDUSER=%s', (iduser,))
    usuario = cur.fetchone()
    cur.close()
    return render_template('cliente/actualizarDatos.html', usuario=usuario)

#Actualizar contraseña
@app.route('/actualizar_contrasena', methods=['POST'])
def actualizar_contrasena():
    iduser = session.get('id')
    if not iduser:
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    actual = request.form.get('actual')
    nueva = request.form.get('nueva')

    if not actual or not nueva:
        flash("⚠️ Debes ingresar ambos campos", "warning")
        return redirect(url_for('actualizarDatos'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT PASS FROM USUARIO WHERE IDUSER = %s', (iduser,))
    row = cur.fetchone()

    if not row:
        flash("❌ Usuario no encontrado", "danger")
        cur.close()
        return redirect(url_for('actualizarDatos'))

    pass_actual = row['PASS']

    # Verificar si la contraseña actual es correcta
    if actual != pass_actual:
        flash("❌ La contraseña actual es incorrecta", "danger")
        cur.close()
        return redirect(url_for('actualizarDatos'))

    # Evitar que la nueva contraseña sea igual a la actual
    if nueva == pass_actual:
        flash("⚠️ La nueva contraseña no puede ser igual a la anterior", "danger")
        cur.close()
        return redirect(url_for('actualizarDatos'))

    # Actualizar contraseña en texto plano
    cur.execute('UPDATE USUARIO SET PASS = %s WHERE IDUSER = %s', (nueva, iduser))
    mysql.connection.commit()
    cur.close()

    flash("✅ Contraseña actualizada correctamente", "success")
    return redirect(url_for('misPedidos'))

#Función Loggout HTML
@app.route('/loggoutCliente')
def loggoutCliente():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 2:
        return redirect(url_for('cerrar_sesion_restringidas'))

    return render_template('cliente/loggoutCliente.html')

#Funcion Loggout Final
@app.route('/cerrar_sesion_cliente')
def cerrar_sesion_cliente():
    # Protección de Ruta
    if not session.get('logueado'):
        flash("⚠️ No hay sesión activa", "warning")
        return redirect(url_for('login'))

    # Verificar rol administrador
    if session.get('rol') != 2:
        return redirect(url_for('cerrar_sesion_restringidas'))

    session.clear()
    flash("✅ Sesión cerrada correctamente", "success")
    return redirect(url_for('index'))


# Cierre de sesión por rutas restringidas
#Función Loggout
@app.route('/cerrar_sesion_restringidas')
def cerrar_sesion_restringidas():
    session.clear()
    flash("🚫 Acceso no autorizado. La sesión fue cerrada.")
    return redirect(url_for('index'))


#Redireccionar si el usuario busca una página no existente
def pagina_no_encontrada(error):
    return redirect(url_for('index'))

#Si estamos desde el archivo inicial (main), se ejecutará la aplicación
if __name__ == '__main__':
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True) #debug=True permite que cualquier cambio se aplique cuando el servidor esta activo