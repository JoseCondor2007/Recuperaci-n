from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import date, datetime

app = Flask(__name__)
# ¡CUIDADO! Esta clave es de ejemplo, debe ser cambiada en producción por una clave segura.
app.secret_key = 'supermercado_delicioso_key' 

# Configuración de la base de datos MySQL
# NOTA: Los detalles de conexión (host, user, password, database)
# deben ser reemplazados con los de tu propia base de datos.
DB_CONFIG = {
    'host': 'supermercado.cnj9i6twcmqf.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'supermercado',
    'database': 'supermercado_db'
}

def get_db_connection():
    """Establece y devuelve una conexión a la base de datos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

@app.route('/')
def index():
    """Ruta para la página principal y el formulario de pedido."""
    return render_template('index.html')

@app.route('/realizar_pedido', methods=['POST'])
def realizar_pedido():
    """
    Maneja el envío del formulario de pedido, valida los datos
    e inserta el nuevo pedido en la base de datos.
    """
    if request.method == 'POST':
        # Obtener los datos del formulario de pedido
        nombre_completo = request.form['nombre_completo']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion_envio = request.form['direccion_envio']
        productos_solicitados = request.form['productos_solicitados']
        notas_adicionales = request.form.get('notas_adicionales', '') # Campo opcional

        errors = {}

        # Validaciones básicas del lado del servidor
        if not nombre_completo.strip():
            errors['nombre_completo'] = 'El nombre completo es un campo obligatorio.'
        if not email.strip():
            errors['email'] = 'El email es un campo obligatorio.'
        if not telefono.strip():
            errors['telefono'] = 'El teléfono es un campo obligatorio.'
        if not direccion_envio.strip():
            errors['direccion_envio'] = 'La dirección de envío es un campo obligatorio.'
        if not productos_solicitados.strip():
            errors['productos_solicitados'] = 'Los productos solicitados son un campo obligatorio.'

        if errors:
            for field, msg in errors.items():
                flash(f'Error en {field}: {msg}', 'error')
            return redirect(url_for('index'))

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # SQL para insertar un nuevo pedido
                # Asegúrate de que la tabla 'pedidos' exista en tu base de datos
                # con las columnas 'nombre_completo', 'email', 'telefono',
                # 'direccion_envio', 'productos_solicitados', 'notas_adicionales', 'fecha_pedido'
                sql = """
                INSERT INTO pedidos (nombre_completo, email, telefono, direccion_envio, productos_solicitados, notas_adicionales, fecha_pedido)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                # La fecha del pedido se generará automáticamente en el servidor
                fecha_pedido = datetime.now()
                cursor.execute(sql, (nombre_completo, email, telefono, direccion_envio, productos_solicitados, notas_adicionales, fecha_pedido))
                conn.commit()

                # Recuperar los datos para mostrarlos en la página de confirmación
                # Para simplificar, usaremos los datos directamente del formulario
                # En un entorno real, podrías recuperar el pedido de la DB por su ID
                pedido_confirmado = {
                    'id': cursor.lastrowid, # ID del pedido recién insertado
                    'nombre_completo': nombre_completo,
                    'email': email,
                    'telefono': telefono,
                    'direccion_envio': direccion_envio,
                    'productos_solicitados': productos_solicitados,
                    'notas_adicionales': notas_adicionales,
                    'fecha_pedido': fecha_pedido.strftime('%d/%m/%Y %H:%M:%S')
                }
                
                return render_template('exito.html', pedido=pedido_confirmado)

            except mysql.connector.Error as err:
                flash(f"Error al guardar el pedido en la base de datos: {err}", 'error')
                conn.rollback() # Deshacer si hay un error
                return redirect(url_for('index'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash("No se pudo conectar a la base de datos. Inténtalo de nuevo más tarde.", 'error')
            return redirect(url_for('index'))

    # Si alguien intenta acceder a /realizar_pedido directamente sin POST
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Para desarrollo: app.run(debug=True)
    # Para producción: app.run(debug=False, host='0.0.0.0')
    app.run(debug=True)
