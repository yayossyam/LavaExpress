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
                    return render_template('administrador/admin.html') #Manda a ruta Admin si se cumple los requisitos
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

#Pedidos
@app.route('/pedidos')
def pedidos():
    return render_template('administrador/pedidos.html')

#Nuevo Pedido
@app.route('/nuevoPedido')
def nuevoPedido():
    return render_template('administrador/nuevoPedido.html')

#Cambiar Estado de Pedido
@app.route('/cambioEstadoPedido')
def cambioEstadoPedido():
    return render_template('administrador/cambioEstadoPedido.html')

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

#Compra Materia Prima
@app.route('/compraMateriaPrima')
def compraMateriaPrima():
    return render_template('administrador/compraMateriaPrima.html')

#Catalogo Productos
@app.route('/catalogoProductos')
def catalogoProductos():
    return render_template('administrador/catalogoProductos.html')

#Nueva Prenda
@app.route('/categoriaPrendas', methods=['GET', 'POST'])
def categoriaPrendas():
    if request.method == 'POST' and 'nombre' in request.form:
        #Capturar los datos ingresados en el form
        #Convertimos los valores en minusculas
        nombre = request.form['nombre'].strip()

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
        cur.execute('INSERT INTO CATEGORIAPRENDAS(IDCATEGORIA, NOMBRE) VALUES (%s, %s)',(id, nombre),)

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

#Editar Prenda
@app.route('/categoriaPrenda/editar_categoria/<int:idcategoria>', methods=['GET', 'POST'])
def editar_categoria(idcategoria):
    #Verificar que el formulario se haya enviado
    if request.method == 'POST':
        
        #Capturamos los datos ingresados
        nombre = request.form['nombre']

        #Creamos instancia BD
        cur = mysql.connection.cursor()

        #Generamos UPDATE
        cur.execute('UPDATE CATEGORIAPRENDAS SET NOMBRE = %s WHERE IDCATEGORIA = %s',(nombre, idcategoria))

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

#Eliminar Prenda
@app.route('/categoriaPrenda/eliminar_categoria/<int:idcategoria>')
def eliminar_categoria(idcategoria):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM CATEGORIAPRENDAS WHERE IDCATEGORIA = %s', (idcategoria,))
    mysql.connection.commit()
    cur.close()

    flash("✅ Categoría eliminada correctamente", "success")
    return redirect(url_for('categoriaPrendas'))
    

#Catalogo de Prendas
@app.route('/catalogoPrendas')
def catalogoPrendas():
    return render_template('administrador/catalogoPrendas.html')

#Cargas
@app.route('/cargas')
def cargas():
    return render_template('administrador/cargas.html')

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
    if request.method == 'POST' and 'nombre' in request.form and 'unidad' in request.form and 'stock' in request.form:

        #Capturamos los datos ingresados en el form
        nombre = request.form['nombre'].strip() #El STRIP elimina espacios al inicio y final
        unidad = request.form['unidad'].strip()
        stock = request.form['stock'].strip()

        #Creamos una instancia de BD para generar consultas
        cur = mysql.connection.cursor()

        #Verificar si ya existe la materia prima
        #El LOWER convierte la informacion ingresada en minusculas y compara
        cur.execute('SELECT * FROM MATERIAPRIMA WHERE LOWER(NOMBREMATERIAPRIMA) = %s',(nombre.lower(),))
        existente = cur.fetchone()

        if existente:
            flash("❌ La materia prima ya existe", "warning")
            return redirect(url_for('materiaPrima'))

        #Obtenemos el ultimo ID 
        cur.execute('SELECT MAX(IDMATERIAPRIMA) AS max_id FROM MATERIAPRIMA')
        result = cur.fetchone()
        id = (result['max_id'] or 0) + 1

        #Generamos INSERT
        cur.execute('INSERT INTO MATERIAPRIMA(IDMATERIAPRIMA, NOMBREMATERIAPRIMA, CANTIDAD, UNIDADMEDIDA, STOCKMINIMO) VALUES (%s, %s, %s, %s, %s)', (id, nombre, 0, unidad, stock),)

        #Guardamos INSERT
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Materia Prima creada de manera éxitosa", "success")
        return redirect(url_for('materiaPrima'))
    
    #SI ES GET MOSTRAMOS MATERIAS PRIMAS EXISTENTES
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDMATERIAPRIMA, NOMBREMATERIAPRIMA, CANTIDAD FROM MATERIAPRIMA')
    materias = cur.fetchall()
    return render_template('administrador/materiaPrima/materiaPrima.html', materias = materias)

#Editar Materia Prima
@app.route('/materiaPrima/editar_materia/<int:idmateriaprima>', methods=['GET', 'POST'])
def editar_materia(idmateriaprima):
    #Verificamos si el método es POST (si le dio actualizar a la tabla de editar materia)
    if request.method == 'POST':

        #Obtener los datos colocados en el formulario editar
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        unidad = request.form['unidad']
        stock = request.form['stock']

        #Creamos instancia para la BD
        cur = mysql.connection.cursor()

        #Ejecutamos la sentencia UPDATE
        cur.execute('UPDATE MATERIAPRIMA SET NOMBREMATERIAPRIMA =%s, CANTIDAD=%s, UNIDADMEDIDA=%s, STOCKMINIMO=%s WHERE IDMATERIAPRIMA = %s',(nombre, cantidad, unidad, stock,idmateriaprima))

        #Guardamos la sentencia
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Dato actualizado correctamente", "success")
        return redirect(url_for('materiaPrima'))

    #SI ES GET,MOSTRAMOS LOS DATOS ACTUALES
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDMATERIAPRIMA, NOMBREMATERIAPRIMA, CANTIDAD, UNIDADMEDIDA, STOCKMINIMO FROM MATERIAPRIMA WHERE IDMATERIAPRIMA=%s', (idmateriaprima,))
    materia = cur.fetchone()
    cur.close()

    return render_template('administrador/materiaPrima/editarMateriaPrima.html', materia = materia)

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
        cur.execute('INSERT INTO SERVICIOPEDIDO (IDSERVICIO, NOMSERVICIO) VALUES (%s, %s)', (id, nombre),)

        #Guardamos INSERT
        mysql.connection.commit()

        #Cerramos BD
        cur.close()

        #Mensaje de éxito
        flash("✅ Tipo de servicio creado de manera éxitosa", "success")
        return redirect(url_for('servicios'))
    
    # Si el metodo es GET, mostramos los datos existentes
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDSERVICIO, NOMSERVICIO FROM SERVICIOPEDIDO')
    servicios = cur.fetchall()

    return render_template('/administrador/servicios/servicios.html', servicios = servicios)

#Editar Servicios
@app.route('/servicios/editar_servicios/<int:idservicio>', methods=['GET', 'POST'])
def editar_servicios(idservicio):
    if request.method == 'POST':
        #Recuperar nuevos datos
        nombre = request.form['nombre']

        #Crear instancia BD
        cur = mysql.connection.cursor()

        #Generar UPDATE
        cur.execute('UPDATE SERVICIOPEDIDO SET NOMSERVICIO = %s WHERE IDSERVICIO = %s', (nombre, idservicio))

        #Guardar UPDATE
        mysql.connection.commit()

        #Cerrar BD
        cur.close()

        #Mensaje éxito
        flash("✅ Dato actualizado correctamente", "success")
        return redirect(url_for('servicios'))
    
    #Si es GET, MUESTRA LOS DATOS A EDITAR
    cur = mysql.connection.cursor()
    cur.execute('SELECT IDSERVICIO, NOMSERVICIO FROM SERVICIOPEDIDO WHERE IDSERVICIO = %s', (idservicio,))
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