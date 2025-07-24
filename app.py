from flask import Flask, render_template, request, redirect
import sqlite3
from proyecto import inicializar_bases

app = Flask(__name__)
inicializar_bases()  # Ejecuta solo una vez al inicio

# Ruta principal
@app.route('/')
def home():
    return render_template('index.html')  # Asegurate de tener este archivo en templates/

@app.route('/tela/taller/agregar-producto', methods=['GET', 'POST'])
def agregar_producto_tela_taller():
    mensaje = None
    conn = sqlite3.connect('database/tela.db')
    c = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()

        seccion_raw = request.form.get('seccion_id')
        seccion_id = int(seccion_raw) if seccion_raw and seccion_raw.isdigit() else None

        # Insertar producto sin cantidad
        c.execute(
            "INSERT INTO productos (nombre, seccion_id) VALUES (?, ?)",
            (nombre, seccion_id)
        )
        producto_id = c.lastrowid

        # Inicializar stock en ambas ubicaciones
        c.execute("INSERT INTO stock_local (producto_id, cantidad) VALUES (?, ?)", (producto_id, 0))
        c.execute("INSERT INTO stock_taller (producto_id, cantidad) VALUES (?, ?)", (producto_id, 0))

        conn.commit()
        mensaje = "✅ Producto registrado y stock inicializado en local y taller."

    secciones = c.execute("SELECT id, nombre FROM secciones").fetchall()
    conn.close()

    return render_template('agregar_producto_tela_taller.html', mensaje=mensaje, secciones=secciones)

@app.route('/tela/taller/modificar-cantidad', methods=['POST'])
def modificar_cantidad_tela_taller():
    producto_id = int(request.form['producto_id'])
    accion = request.form['accion']
    seccion_abierta = request.form.get('seccion_abierta')

    print("==> Solicitud recibida:")
    print("Producto:", producto_id, "Acción:", accion, "Sección abierta:", seccion_abierta)

    conn = sqlite3.connect('database/tela.db')
    c = conn.cursor()

    # Verificar si existe entrada en stock_taller
    c.execute("SELECT cantidad FROM stock_taller WHERE producto_id = ?", (producto_id,))
    resultado = c.fetchone()

    if resultado:
        cantidad_actual = resultado[0]
        print("Cantidad actual:", cantidad_actual)

        if accion == 'sumar':
            nueva_cantidad = cantidad_actual + 1
        elif accion == 'restar':
            nueva_cantidad = max(0, cantidad_actual - 1)
        else:
            nueva_cantidad = cantidad_actual

        print("Nueva cantidad:", nueva_cantidad)

        c.execute("UPDATE stock_taller SET cantidad = ? WHERE producto_id = ?", (nueva_cantidad, producto_id))
        conn.commit()
        print("✅ Stock actualizado.")

    else:
        print("⚠️ Producto no encontrado en stock_taller.")

    conn.close()
    return redirect(f"/tela/taller/consultar-stock?abierta={seccion_abierta}")

@app.route('/tela/taller/consultar-stock')
def consultar_stock_tela_taller():
    conn = sqlite3.connect('database/tela.db')
    c = conn.cursor()
    filtro = request.args.get('buscar')

    query = '''
        SELECT productos.id, productos.nombre,
               stock_taller.cantidad,
               secciones.nombre
        FROM productos
        LEFT JOIN secciones ON productos.seccion_id = secciones.id
        LEFT JOIN stock_taller ON productos.id = stock_taller.producto_id
    '''
    params = ()
    if filtro:
        query += ' WHERE productos.nombre LIKE ? OR secciones.nombre LIKE ?'
        params = (f'%{filtro}%', f'%{filtro}%')

    query += ' ORDER BY secciones.nombre, productos.nombre'
    resultados = c.execute(query, params).fetchall()
    conn.close()

    stock_por_seccion = {}

    for id_prod, nombre_prod, cantidad, nombre_seccion in resultados:
        clave = nombre_seccion if nombre_seccion else "🗂️ Sin sección"
        stock_por_seccion.setdefault(clave, {'total': 0, 'productos': []})
        stock_por_seccion[clave]['productos'].append({
            'id': id_prod,
            'nombre': nombre_prod,
            'cantidad': cantidad or 0
        })
        stock_por_seccion[clave]['total'] += cantidad or 0

    return render_template('consultar_stock_tela_taller.html',
                           stock_por_seccion=stock_por_seccion,
                           filtro=filtro)


@app.route('/tela/local/consultar-stock')
def consultar_stock_tela_local():
    conn = sqlite3.connect('database/tela.db')
    c = conn.cursor()
    filtro = request.args.get('buscar')

    query = '''
        SELECT productos.id, productos.nombre,
               stock_local.cantidad,
               secciones.nombre
        FROM productos
        LEFT JOIN secciones ON productos.seccion_id = secciones.id
        LEFT JOIN stock_local ON productos.id = stock_local.producto_id
    '''
    params = ()
    if filtro:
        query += ' WHERE productos.nombre LIKE ? OR secciones.nombre LIKE ?'
        params = (f'%{filtro}%', f'%{filtro}%')

    query += ' ORDER BY secciones.nombre, productos.nombre'
    resultados = c.execute(query, params).fetchall()
    conn.close()

    stock_por_seccion = {}

    for id_prod, nombre_prod, cantidad, nombre_seccion in resultados:
        clave = nombre_seccion if nombre_seccion else "🗂️ Sin sección"
        stock_por_seccion.setdefault(clave, {'total': 0, 'productos': []})
        stock_por_seccion[clave]['productos'].append({
            'id': id_prod,
            'nombre': nombre_prod,
            'cantidad': cantidad or 0
        })
        stock_por_seccion[clave]['total'] += cantidad or 0

    return render_template('consultar_stock_tela_local.html',
                           stock_por_seccion=stock_por_seccion,
                           filtro=filtro)

@app.route('/tela/taller/agregar-seccion', methods=['GET', 'POST'])
def agregar_seccion_tela_taller():
    mensaje = None

    if request.method == 'POST':
        nombre = request.form['nombre']

        conn = sqlite3.connect('database/tela.db')
        c = conn.cursor()
        c.execute("INSERT INTO secciones (nombre) VALUES (?)", (nombre,))
        conn.commit()
        conn.close()

        mensaje = "✅ Sección agregada correctamente."

    return render_template('agregar_seccion_tela_taller.html', mensaje=mensaje)

@app.route('/tela/local/modificar-cantidad', methods=['POST'])
def modificar_cantidad_tela_local():
    producto_id = int(request.form['producto_id'])
    accion = request.form['accion']
    seccion_abierta = request.form.get('seccion_abierta')

    conn = sqlite3.connect('database/tela.db')
    c = conn.cursor()

    # Inicializar si no existe
    c.execute("SELECT COUNT(*) FROM stock_local WHERE producto_id = ?", (producto_id,))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO stock_local (producto_id, cantidad) VALUES (?, ?)", (producto_id, 0))
        conn.commit()

    c.execute("SELECT cantidad FROM stock_local WHERE producto_id = ?", (producto_id,))
    resultado = c.fetchone()

    if resultado:
        cantidad_actual = resultado[0]
        nueva_cantidad = cantidad_actual + 1 if accion == 'sumar' else max(0, cantidad_actual - 1)
        c.execute("UPDATE stock_local SET cantidad = ? WHERE producto_id = ?", (nueva_cantidad, producto_id))
        conn.commit()

    conn.close()
    return redirect(f"/tela/local/consultar-stock?abierta={seccion_abierta}")

@app.route('/madera/taller/agregar-producto', methods=['GET', 'POST'])
def agregar_producto_madera_taller():
    mensaje = None
    conn = sqlite3.connect('database/madera.db')
    c = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()

        seccion_raw = request.form.get('seccion_id')
        seccion_id = int(seccion_raw) if seccion_raw and seccion_raw.isdigit() else None

        # Insertar producto
        c.execute("INSERT INTO productos (nombre, seccion_id) VALUES (?, ?)", (nombre, seccion_id))
        producto_id = c.lastrowid

        # Inicializar stock en local y taller
        c.execute("INSERT INTO stock_local (producto_id, cantidad) VALUES (?, ?)", (producto_id, 0))
        c.execute("INSERT INTO stock_taller (producto_id, cantidad) VALUES (?, ?)", (producto_id, 0))

        conn.commit()
        mensaje = "✅ Producto registrado en madera y stock inicializado."

    secciones = c.execute("SELECT id, nombre FROM secciones").fetchall()
    conn.close()

    return render_template('agregar_producto_madera_taller.html', mensaje=mensaje, secciones=secciones)

@app.route('/madera/taller/modificar-cantidad', methods=['POST'])
def modificar_cantidad_madera_taller():
    producto_id = int(request.form['producto_id'])
    accion = request.form['accion']
    seccion_abierta = request.form.get('seccion_abierta')

    conn = sqlite3.connect('database/madera.db')
    c = conn.cursor()

    # Inicializar si no existe
    c.execute("SELECT COUNT(*) FROM stock_taller WHERE producto_id = ?", (producto_id,))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO stock_taller (producto_id, cantidad) VALUES (?, ?)", (producto_id, 0))
        conn.commit()

    c.execute("SELECT cantidad FROM stock_taller WHERE producto_id = ?", (producto_id,))
    resultado = c.fetchone()

    if resultado:
        cantidad_actual = resultado[0]
        nueva_cantidad = cantidad_actual + 1 if accion == 'sumar' else max(0, cantidad_actual - 1)
        c.execute("UPDATE stock_taller SET cantidad = ? WHERE producto_id = ?", (nueva_cantidad, producto_id))
        conn.commit()

    conn.close()
    return redirect(f"/madera/taller/consultar-stock?abierta={seccion_abierta}")

@app.route('/madera/taller/consultar-stock')
def consultar_stock_madera_taller():
    conn = sqlite3.connect('database/madera.db')
    c = conn.cursor()
    filtro = request.args.get('buscar')

    query = '''
        SELECT productos.id, productos.nombre,
               stock_taller.cantidad,
               secciones.nombre
        FROM productos
        LEFT JOIN secciones ON productos.seccion_id = secciones.id
        LEFT JOIN stock_taller ON productos.id = stock_taller.producto_id
    '''
    params = ()
    if filtro:
        query += ' WHERE productos.nombre LIKE ? OR secciones.nombre LIKE ?'
        params = (f'%{filtro}%', f'%{filtro}%')

    query += ' ORDER BY secciones.nombre, productos.nombre'
    resultados = c.execute(query, params).fetchall()
    conn.close()

    stock_por_seccion = {}

    for id_prod, nombre_prod, cantidad, nombre_seccion in resultados:
        clave = nombre_seccion if nombre_seccion else "🗂️ Sin sección"
        stock_por_seccion.setdefault(clave, {'total': 0, 'productos': []})
        stock_por_seccion[clave]['productos'].append({
            'id': id_prod,
            'nombre': nombre_prod,
            'cantidad': cantidad or 0
        })
        stock_por_seccion[clave]['total'] += cantidad or 0

    return render_template('consultar_stock_madera_taller.html',
                           stock_por_seccion=stock_por_seccion,
                           filtro=filtro)


@app.route('/madera/taller/agregar-seccion', methods=['GET', 'POST'])
def agregar_seccion_madera_taller():
    mensaje = None

    if request.method == 'POST':
        nombre = request.form['nombre']

        conn = sqlite3.connect('database/madera.db')
        c = conn.cursor()
        c.execute("INSERT INTO secciones (nombre) VALUES (?)", (nombre,))
        conn.commit()
        conn.close()

        mensaje = "✅ Sección agregada correctamente en madera."

    return render_template('agregar_seccion_madera_taller.html', mensaje=mensaje)

@app.route('/madera/local/consultar-stock')
def consultar_stock_madera_local():
    conn = sqlite3.connect('database/madera.db')
    c = conn.cursor()
    filtro = request.args.get('buscar')

    query = '''
        SELECT productos.id, productos.nombre,
               stock_local.cantidad,
               secciones.nombre
        FROM productos
        LEFT JOIN secciones ON productos.seccion_id = secciones.id
        LEFT JOIN stock_local ON productos.id = stock_local.producto_id
    '''
    params = ()
    if filtro:
        query += ' WHERE productos.nombre LIKE ? OR secciones.nombre LIKE ?'
        params = (f'%{filtro}%', f'%{filtro}%')

    query += ' ORDER BY secciones.nombre, productos.nombre'
    resultados = c.execute(query, params).fetchall()
    conn.close()

    stock_por_seccion = {}

    for id_prod, nombre_prod, cantidad, nombre_seccion in resultados:
        clave = nombre_seccion if nombre_seccion else "🗂️ Sin sección"
        stock_por_seccion.setdefault(clave, {'total': 0, 'productos': []})
        stock_por_seccion[clave]['productos'].append({
            'id': id_prod,
            'nombre': nombre_prod,
            'cantidad': cantidad or 0
        })
        stock_por_seccion[clave]['total'] += cantidad or 0

    return render_template('consultar_stock_madera_local.html',
                           stock_por_seccion=stock_por_seccion,
                           filtro=filtro)


@app.route('/madera/local/modificar-cantidad', methods=['POST'])
def modificar_cantidad_madera_local():
    producto_id = int(request.form['producto_id'])
    accion = request.form['accion']
    seccion_abierta = request.form.get('seccion_abierta')

    conn = sqlite3.connect('database/madera.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM stock_local WHERE producto_id = ?", (producto_id,))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO stock_local (producto_id, cantidad) VALUES (?, ?)", (producto_id, 0))
        conn.commit()

    c.execute("SELECT cantidad FROM stock_local WHERE producto_id = ?", (producto_id,))
    resultado = c.fetchone()

    if resultado:
        cantidad_actual = resultado[0]
        nueva_cantidad = cantidad_actual + 1 if accion == 'sumar' else max(0, cantidad_actual - 1)
        c.execute("UPDATE stock_local SET cantidad = ? WHERE producto_id = ?", (nueva_cantidad, producto_id))
        conn.commit()

    conn.close()
    return redirect(f"/madera/local/consultar-stock?abierta={seccion_abierta}")



if __name__ == '__main__':
    app.run(debug=True)
