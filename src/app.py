from flask import Flask
from flask import render_template, request, redirect, flash, url_for, Response, session,jsonify
from flask_mysqldb import MySQL, MySQLdb #Instancia de la DB
from config import DB_CONFIG, SECRET_KEY
from bcrypt import checkpw
from datetime import date
import json

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
                session['rol'] = account['IDROL']

                #Identificación de rol
                if account['IDROL'] == 1: #Rol administrativo
                    return redirect(url_for('inicioAdmin')) #Manda a ruta Admin si se cumple los requisitos
                else: #Rol cliente
                    return render_template('cliente/client.html')
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

        flash("✅Usuario Registrado de manera exitosa","success")
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

#Funcion de Reportes
@app.route('/reporte')
def inicioreporte():
    return render_template('administrador/reportes/index.html')

#Administrador
#Crear Usuarios     
@app.route('/inicioAdmin', methods=['GET', 'POST'])
def inicioAdmin():
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
    cur = mysql.connection.cursor()

    #Necesitamos CONCATENAR USUARIO Y ROLES
    cur.execute("""SELECT u.IDUSER, CONCAT(u.NOMBRE, ' ', u.APATERNO) AS nombre_completo, r.NOMROL FROM USUARIO u JOIN ROLES r ON u.IDROL = r.IDROL """)
    usuarios = cur.fetchall()
    cur.close()
    return render_template('administrador/nuevoUsuario/verUsuarios.html', usuarios = usuarios)

#Editar Usuario
@app.route('/verUsuarios/editar_usuarios/<int:idusuario>', methods=['GET', 'POST'])
def editar_usuarios(idusuario):
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
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM USUARIO WHERE IDUSER = %s', (idusuario,))
    mysql.connection.commit()
    cur.close()

    flash("✅ Usuario eliminado correctamente", "success")

    return redirect(url_for('verUsuarios'))

# MOSTRAR PEDIDOS (solo lectura)
@app.route('/pedidos')
def pedidos():
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

                if idcat not in categorias:
                    categorias[idcat] = {'peso': 0, 'preciokg': preciokg}
                
                categorias[idcat]['peso'] += float(p['peso'])
                total_peso += float(p['peso'])

            # Total por categoria
            for cat in categorias.values():
                total_costo += cat['peso'] * cat['preciokg']

            # Costo adicional por servicio
            cur.execute("SELECT COSTO_KG FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s", (idservicio,))
            servicio = cur.fetchone()
            if servicio:
                total_costo += total_peso * float(servicio['COSTO_KG'])

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
            cur.close()

            return jsonify({"success": True, "message": f"Pedido registrado. Total: ${total_costo:.2f}", "idpedido": idpedido})

    except Exception as e:
        mysql.connection.rollback()
        print(f"❌ Error en POST /nuevoPedido: {e}")
        return jsonify({"success": False, "message": "Ocurrió un error al guardar el pedido", "error": str(e)}), 500

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


@app.route('/cambioEstadoPedido', methods=['GET', 'POST'])
def cambioEstadoPedido():
    cur = mysql.connection.cursor()  # cursor normal

    if request.method == 'POST':
        data = request.get_json()  # leer JSON enviado por fetch
        if not data or 'id_pedido' not in data or 'nuevo_estatus' not in data:
            return jsonify({"success": False, "msg": "Datos incompletos"}), 400

        id_pedido = data['id_pedido']
        nuevo_estatus = int(data['nuevo_estatus'])

        # Verificar si el pedido existe
        cur.execute("SELECT IDESTATUS FROM PEDIDOS WHERE IDPEDIDO = %s", (id_pedido,))
        pedido = cur.fetchone()

        if not pedido:
            cur.close()
            return jsonify({"success": False, "msg": "Pedido no encontrado"}), 404

        estatus_actual = int(pedido[0])

        # Verificar que no esté listo
        if estatus_actual == 3:
            cur.close()
            return jsonify({"success": False, "msg": "El pedido ya está 'Listo'"}), 400

        # Validar avance solo 1 nivel
        if nuevo_estatus != estatus_actual + 1:
            cur.close()
            return jsonify({"success": False, "msg": "Solo se puede avanzar un nivel"}), 400

        # Actualizar estado
        cur.execute("""
            UPDATE PEDIDOS SET IDESTATUS = %s WHERE IDPEDIDO = %s
        """, (nuevo_estatus, id_pedido))
        mysql.connection.commit()
        cur.close()

        return jsonify({"success": True})

    # GET: mostrar tabla de pedidos
    id_buscar = request.args.get('id_pedido', '')

    base_query = """
        SELECT 
            p.IDPEDIDO,
            CONCAT(u.NOMBRE, ' ', u.APATERNO) AS NOMBRECLIENTE,
            p.IDESTATUS,
            e.NOMESTATUS
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
    pedidos = cur.fetchall()  # lista de tuplas

    # Lista de estatus
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
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM PROVEEDORES WHERE IDPROVEEDOR = %s', (idproveedor,))
    mysql.connection.commit()
    cur.close()
    flash('✅ Proveedor eliminado correctamente','success')
    return redirect(url_for('proveedores'))

# Compra Materia Prima
@app.route('/compraMateriaPrima', methods=['GET', 'POST'])
def compraMateriaPrima():
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
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM CATEGORIAPRENDAS WHERE IDCATEGORIA = %s', (idcategoria,))
    mysql.connection.commit()
    cur.close()

    flash("✅ Categoría eliminada correctamente", "success")
    return redirect(url_for('categoriaPrendas'))

#Nueva Prenda
@app.route('/catalogoPrendas', methods=['GET', 'POST'])
def catalogoPrendas():
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
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM CATALOGOPRENDAS WHERE IDCATALOGO = %s',(idcatalogo,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Prenda eliminada correctamente", "success")

    return redirect(url_for('catalogoPrendas'))

# RUTA: CARGAS
@app.route('/cargas', methods=['GET', 'POST'])
def cargas():
    if request.method == 'POST':
        idcategoria = request.form['idcategoria']
        id_materias_list = request.form.getlist('idmateria')
        cargas_list = request.form.getlist('carga')

        if not idcategoria or not id_materias_list:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('cargas'))

        cur = mysql.connection.cursor()
        exitosas = 0
        fallidas = 0

        for id_materia, carga_cantidad in zip(id_materias_list, cargas_list):
            try:
                id_materia = int(id_materia)
                carga_cantidad = float(carga_cantidad)
                id_categoria_int = int(idcategoria)
            except ValueError:
                fallidas += 1
                continue

            # Obtener último ID
            cur.execute('SELECT MAX(IDCLAVE) AS max_id FROM CARGAS')
            resultado = cur.fetchone()
            idclave = (resultado['max_id'] or 0) + 1

            # Verificar existencia
            cur.execute('SELECT NOMBREMATERIAPRIMA FROM MATERIAPRIMA WHERE IDMATERIAPRIMA = %s', (id_materia,))
            materia_info = cur.fetchone()
            nombre_materia = materia_info['NOMBREMATERIAPRIMA'] if materia_info else f"ID {id_materia}"


            cur.execute('INSERT INTO CARGAS(IDCLAVE, IDCATEGORIA, IDMATERIAPRIMA, DESCPORCARGA) VALUES (%s, %s, %s, %s)',
                        (idclave, id_categoria_int, id_materia, carga_cantidad))
            exitosas += 1

        mysql.connection.commit()
        cur.close()

        if exitosas > 0:
            flash(f"Registro de Carga(s) exitoso. Se insertaron {exitosas} fila(s).", "success")
        if fallidas > 0 and exitosas == 0:
            flash(f"No se pudo registrar ninguna carga. Revisa las advertencias.", "danger")

        return redirect(url_for('cargas'))

    # GET
    cur = mysql.connection.cursor()

    # Cargas existentes
    cur.execute('''
        SELECT 
            c.IDCLAVE,
            c.IDCATEGORIA,
            cat.NOMBRE AS CATEGORIA,
            CONCAT(
                m.NOMBREMATERIAPRIMA, ' ',
                TRIM(TRAILING '.00' FROM 
                    (CASE 
                        WHEN m.CANTIDADUM = FLOOR(m.CANTIDADUM) THEN CAST(FORMAT(m.CANTIDADUM, 0) AS CHAR)
                        ELSE CAST(m.CANTIDADUM AS CHAR)
                    END)
                ), ' ',
                (CASE 
                    WHEN m.CANTIDADUM = 1 THEN TRIM(TRAILING 's' FROM u.NOMBRE)
                    ELSE u.NOMBRE
                END)
            ) AS MATERIA,
            c.DESCPORCARGA
        FROM CARGAS c
        JOIN CATEGORIAPRENDAS cat ON cat.IDCATEGORIA = c.IDCATEGORIA
        JOIN MATERIAPRIMA m ON m.IDMATERIAPRIMA = c.IDMATERIAPRIMA
        JOIN UNIDADESMEDIDA u ON u.IDUNIDAD = m.IDUNIDAD
        ORDER BY cat.NOMBRE ASC, c.IDCLAVE ASC
    ''')


    cargas = cur.fetchall()

    # Agrupar por categoría para rowspan
    cargas_agrupadas = {}
    categorias_con_carga = set()
    for c in cargas:
        cat = c['CATEGORIA']
        if cat not in cargas_agrupadas:
            cargas_agrupadas[cat] = []
        cargas_agrupadas[cat].append(c)
        categorias_con_carga.add(c['CATEGORIA'])

    # Categorías
    cur.execute('SELECT IDCATEGORIA, NOMBRE FROM CATEGORIAPRENDAS ORDER BY NOMBRE ASC')
    todas_categorias = cur.fetchall()
    categorias = [cat for cat in todas_categorias if cat['NOMBRE'] not in categorias_con_carga]

    # Materias primas sin carga
    cur.execute('SELECT IDMATERIAPRIMA, NOMBREMATERIAPRIMA FROM MATERIAPRIMA ORDER BY NOMBREMATERIAPRIMA ASC')
    materias = cur.fetchall()

    cur.close()

    return render_template('administrador/cargas/cargas.html', cargas_agrupadas=cargas_agrupadas, categorias=categorias, materias=materias)

# AUTOCOMPLETADO MATERIA PRIMA
@app.route('/buscar_materia')
def buscar_materia():
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

#Editar Carga
@app.route('/cargas/editar_carga/<int:idcategoria>', methods=['GET', 'POST'])
def editar_carga(idcategoria):
    if request.method == 'POST':

        #Capturar el form
        id_materias = request.form.getlist('idmateria')
        cargas_list = request.form.getlist('carga')

        #Crear instancia BD
        cur = mysql.connection.cursor()

        #Eliminar cargas actuales
        cur.execute('DELETE FROM CARGAS WHERE IDCATEGORIA = %s', (idcategoria,))

        #Insertar nuevas materias
        for id_materia, carga_cantidad in zip(id_materias, cargas_list):
            try:
                id_materia = int(id_materia)
                carga_cantidad = float(carga_cantidad)
            except ValueError:
                continue

            cur.execute('SELECT MAX(IDCLAVE) AS max_id FROM CARGAS')
            resultado = cur.fetchone()
            idclave = (resultado['max_id'] or 0) + 1

            cur.execute('INSERT INTO CARGAS(IDCLAVE, IDCATEGORIA, IDMATERIAPRIMA, DESCPORCARGA) VALUES (%s, %s, %s, %s)',(idclave, idcategoria, id_materia, carga_cantidad))

        
        mysql.connection.commit()
        cur.close()
        flash("Carga Actualizada Correctamente", "success")
        return redirect(url_for('cargas'))
    
    #Si es GET
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT 
            c.IDMATERIAPRIMA,
            m.NOMBREMATERIAPRIMA,
            m.CANTIDADUM,
            u.NOMBRE AS UNIDAD,
            CONCAT(
                m.NOMBREMATERIAPRIMA, ' ',
                TRIM(TRAILING '.00' FROM 
                    (CASE 
                        WHEN m.CANTIDADUM = FLOOR(m.CANTIDADUM) THEN CAST(FORMAT(m.CANTIDADUM, 0) AS CHAR)
                        ELSE CAST(m.CANTIDADUM AS CHAR)
                    END)
                ), ' ',
                (CASE 
                    WHEN m.CANTIDADUM = 1 THEN TRIM(TRAILING 's' FROM u.NOMBRE)
                    ELSE u.NOMBRE
                END)
            ) AS NOMBRE_COMPLETO,
            c.DESCPORCARGA,
            cat.NOMBRE AS CATEGORIA
        FROM CARGAS c
        JOIN MATERIAPRIMA m ON c.IDMATERIAPRIMA = m.IDMATERIAPRIMA
        JOIN UNIDADESMEDIDA u ON m.IDUNIDAD = u.IDUNIDAD
        JOIN CATEGORIAPRENDAS cat ON c.IDCATEGORIA = cat.IDCATEGORIA
        WHERE c.IDCATEGORIA = %s
    ''', (idcategoria,))
    cargas_actuales = cur.fetchall()

    # Materias primas disponibles
    cur.execute('SELECT IDMATERIAPRIMA, NOMBREMATERIAPRIMA FROM MATERIAPRIMA ORDER BY NOMBREMATERIAPRIMA ASC')
    materias = cur.fetchall()
    cur.close()

    return render_template('administrador/cargas/editar_carga.html', cargas = cargas_actuales, materias = materias, idcategoria = idcategoria)

#Eliminar Carga
@app.route('/cargas/eliminar_carga/<int:idcategoria>', methods=['GET'])
def eliminar_carga(idcategoria):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM CARGAS WHERE IDCATEGORIA = %s", (idcategoria,))
    mysql.connection.commit()
    cur.close()
    flash("Carga eliminada correctamente.", "success")
    return redirect(url_for('cargas'))

#Reportes
@app.route('/reportes')
def reportes():
    return render_template('administrador/reportes/index.html')

#Reportes Ventas
@app.route('/reportesVentas')
def reportes_ventas():
    return render_template('administrador/reportes/reportesVentas.html')

#Reportes Reabastecimiento
@app.route('/reportesReabastecimiento')
def reportes_reabastecimiento():
    return render_template('administrador/reportes/reportesReabastecimiento.html')

#Reportes Tickets
@app.route('/reportesTicket')
def reportes_tickets():
    return render_template('administrador/reportes/reportesTicket.html')

#Reportes Inventario
@app.route('/reportesInventario')
def reportes_inventario():
    return render_template('administrador/reportes/reportesInventario.html')

#Roles
@app.route('/roles', methods=['GET', 'POST'])
def roles():
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
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM ROLES WHERE IDROL=%s', (idrol,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Rol eliminado correctamente", "success")
    return redirect(url_for('roles'))

#Nueva Materia Prima
@app.route('/materiaPrima', methods=['GET', 'POST'])
def materiaPrima():
    if request.method == 'POST' and 'nombre' in request.form and 'stock' in request.form and 'unidad' in request.form and 'cantidadum' in request.form:

        #Capturamos los datos ingresados en el form
        nombre = request.form['nombre'].strip() #El STRIP elimina espacios al inicio y final
        stock = request.form['stock'].strip()
        unidad = request.form['unidad'].strip()
        cantidadum = request.form['cantidadum'].strip()

        #Creamos una instancia de BD para generar consultas
        cur = mysql.connection.cursor()

        #Verificar si ya existe la materia prima
        #El LOWER convierte la informacion ingresada en minusculas y compara
        cur.execute('SELECT * FROM MATERIAPRIMA WHERE LOWER(NOMBREMATERIAPRIMA) = %s AND IDUNIDAD = %s AND CANTIDADUM = %s',(nombre.lower(), unidad, cantidadum))
        existente = cur.fetchone()

        if existente:
            flash("❌ La materia prima con esa unidad y cantidad ya existe", "danger")
            return redirect(url_for('materiaPrima'))

        #Obtenemos el ultimo ID 
        cur.execute('SELECT MAX(IDMATERIAPRIMA) AS max_id FROM MATERIAPRIMA')
        result = cur.fetchone()
        id = (result['max_id'] or 0) + 1

        #Generamos INSERT
        cur.execute('INSERT INTO MATERIAPRIMA(IDMATERIAPRIMA, NOMBREMATERIAPRIMA, CANTIDAD, STOCKMINIMO, IDUNIDAD, CANTIDADUM) VALUES (%s, %s, %s, %s, %s, %s)', (id, nombre, 0, stock, unidad, cantidadum))

        #Guardamos INSERT
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Materia Prima creada de manera éxitosa", "success")
        return redirect(url_for('materiaPrima'))
    
    #SI ES GET MOSTRAMOS MATERIAS PRIMAS EXISTENTES
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT mp.IDMATERIAPRIMA, mp.NOMBREMATERIAPRIMA, mp.CANTIDAD, mp.CANTIDADUM, u.NOMBRE AS UNIDAD 
        FROM MATERIAPRIMA mp 
        JOIN UNIDADESMEDIDA u ON mp.IDUNIDAD = u.IDUNIDAD
        ORDER BY mp.NOMBREMATERIAPRIMA
    ''')
    materias = cur.fetchall()

    cur.execute('SELECT IDUNIDAD, NOMBRE FROM UNIDADESMEDIDA')
    unidadess = cur.fetchall()
    cur.close()
    return render_template('administrador/materiaPrima/materiaPrima.html', materias = materias, unidadess = unidadess)

#Editar Materia Prima
@app.route('/materiaPrima/editar_materia/<int:idmateriaprima>', methods=['GET', 'POST'])
def editar_materia(idmateriaprima):
    #Verificamos si el método es POST (si le dio actualizar a la tabla de editar materia)
    if request.method == 'POST':

        #Obtener los datos colocados en el formulario editar
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        stock = request.form['stock']
        unidad = request.form['unidad']
        cantidadum = request.form['cantidadum']

        #Creamos instancia para la BD
        cur = mysql.connection.cursor()

        #Ejecutamos la sentencia UPDATE
        cur.execute('UPDATE MATERIAPRIMA SET NOMBREMATERIAPRIMA =%s, CANTIDAD=%s, STOCKMINIMO=%s, IDUNIDAD = %s, CANTIDADUM = %s WHERE IDMATERIAPRIMA = %s',(nombre, cantidad, stock, unidad, cantidadum, idmateriaprima))

        #Guardamos la sentencia
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Dato actualizado correctamente", "success")
        return redirect(url_for('materiaPrima'))

    #SI ES GET,MOSTRAMOS LOS DATOS ACTUALES
    cur = mysql.connection.cursor()
    cur.execute('SELECT mp.IDMATERIAPRIMA, mp.NOMBREMATERIAPRIMA, mp.CANTIDAD, mp.STOCKMINIMO, mp.CANTIDADUM, u.IDUNIDAD, u.NOMBRE FROM MATERIAPRIMA mp JOIN UNIDADESMEDIDA u ON mp.IDUNIDAD = u.IDUNIDAD WHERE mp.IDMATERIAPRIMA=%s', (idmateriaprima,))
    materia = cur.fetchone()
    
    cur.execute('SELECT IDUNIDAD, NOMBRE FROM UNIDADESMEDIDA')
    unidades = cur.fetchall()
    cur.close()

    return render_template('administrador/materiaPrima/editarMateriaPrima.html', materia = materia, unidades= unidades)

#Eliminar MateriaPrima
@app.route('/materiaPrima/eliminar_materia/<int:idmateriaprima>',methods=['GET'])
def eliminar_materia(idmateriaprima):
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
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s', (idservicio,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Tipo de servicio eliminado correctamente", "success")
    return redirect(url_for('servicios'))

#Nuevo Estatus
@app.route('/estatus', methods=['GET', 'POST'])
def estatus():
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
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM ESTATUSPEDIDO WHERE IDESTATUS = %s', (idestatus,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Tipo de estatus eliminado correctamente", "success")

    return redirect(url_for('estatus'))

#Nueva Unidad de Medida
@app.route('/unidadesMedidas', methods=['GET', 'POST'])
def unidadesMedidas():
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
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM UNIDADESMEDIDA WHERE IDUNIDAD = %s', (idunidad,))
    mysql.connection.commit()
    cur.close()
    flash("✅ Unidad de medida eliminado correctamente", "success")

    return redirect(url_for('unidadesMedidas'))

#Función Loggout
@app.route('/loggoutAdmin')
def loggout():
    return render_template('administrador/loggoutAdmin.html')





#Cliente
#Función Mis Pedidos
@app.route('/misPedidos')
def misPedidos():
    return render_template('cliente/misPedidos.html')

#Función Actualizar Datos
@app.route('/actualizarDatos')
def actualizarDatos():
    return render_template('cliente/actualizarDatos.html')

#Función Loggout
@app.route('/loggoutCliente')
def loggoutCliente():
    return render_template('cliente/loggoutCliente.html')


#Redireccionar si el usuario busca una página no existente
def pagina_no_encontrada(error):
    return redirect(url_for('index'))

#Si estamos desde el archivo inicial (main), se ejecutará la aplicación
if __name__ == '__main__':
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True) #debug=True permite que cualquier cambio se aplique cuando el servidor esta activo