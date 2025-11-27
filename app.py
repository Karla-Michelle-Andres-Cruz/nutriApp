from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TIAMIOSSOTT12'

# Configuración MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'usuarios'


mysql = MySQL(app)

def email_existe(email):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error verificando email: {e}")
        return False


def obtener_usuario_por_email(email):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
        return cursor.fetchone()
    except Exception as e:
        print(f"error verificando usuario: {e}")
        return None






# ================================================
#               RUTAS PRINCIPALES
# ================================================

@app.route('/')
@app.route('/ini')
def inicio():
    usuario = session.get("usuario_email")
    return render_template("inicio.html", usuario=usuario)


# ================================================
#               PERFIL DE USUARIO
# ================================================

@app.route('/perfil')
def perfil():
    if 'usuario_email' not in session:
        flash("Inicia sesión para ver tu perfil", "error")
        return redirect(url_for('sesion'))

    usuario_id = session['usuario_id']
    cur = mysql.connection.cursor()

    # Usuario como tupla
    cur.execute("SELECT * FROM usuarios WHERE id=%s", (usuario_id,))
    usuario = cur.fetchone()

    # Salud como tupla
    cur.execute("SELECT * FROM perfiles_usuario WHERE usuario_id=%s", (usuario_id,))
    salud = cur.fetchone()

    cur.close()

    return render_template("perfilUsuarios.html", usuario=usuario, salud=salud)





# ================================================
#               REGISTRO DE USUARIOS
# ================================================

@app.route("/registro")
def registro():
    dias = list(range(1, 32))
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    año_actual = datetime.now().year
    años = list(range(año_actual, 1905, -1))

    return render_template("registro.html", dias=dias, meses=meses, años=años)


@app.route("/registrame", methods=["POST"])
def registrame():
    nombre = request.form["nombre"]
    paterno = request.form["paterno"]
    materno = request.form["materno"]
    email = request.form["email"]
    password = request.form["password"]
    confirm = request.form["confirmaContraseña"]
    fecha_nacimiento = request.form.get("fecha_nacimiento")
    genero = request.form.get("genero")
    telefono = request.form.get("telefono")

    # Validar que coincidan las contraseñas
    if password != confirm:
        flash("Las contraseñas no coinciden", "danger")
        return redirect(url_for("registro"))

    try:
        cursor = mysql.connection.cursor()

        # Hashear la contraseña
        hashed_password = generate_password_hash(password)

        # INSERT corregido
        cursor.execute(
            'INSERT INTO usuarios (email, password, nombre, paterno, materno, fecha_nacimiento, genero, telefono) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
            (email, hashed_password, nombre, paterno, materno, fecha_nacimiento, genero, telefono)
        )

        mysql.connection.commit()
        cursor.close()

        flash("¡Registro exitoso!", "success")
        return redirect(url_for("sesion"))

    except Exception as e:
        flash(f"Error al registrar usuario: {str(e)}", "danger")
        return redirect(url_for("registro"))



# ================================================
#                   LOGIN
# ================================================

@app.route("/iniciosesion")
def sesion():
    if session.get('logueado'):
        return redirect(url_for("inicio"))
    return render_template("sesion.html")


@app.route("/validalogin", methods=['POST'])
def validaLogin():
    if 'usuario_id' in session:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Por favor ingrese email y contraseña', 'danger')
            return render_template('sesion.html')
        
        usuario = obtener_usuario_por_email(email)

        if usuario:

            # usuario[2] == email, usuario[3] == password
            if check_password_hash(usuario[2], password):
                session['usuario_id'] = usuario[0]
                session['usuario_nombre'] = usuario[3]
                session['usuario_email'] = usuario[1]

                flash(f'¡Bienvenido {usuario[3]}!', 'success')
                return redirect(url_for('inicio'))
            else:
                flash('Contraseña incorrecta', 'danger')
                return render_template('sesion.html')  # ← FALTABA ESTO
        else:
            flash('El correo no esta registrado', 'danger')
            return render_template('sesion.html')



@app.route("/cerrarsesion")
def cerrarsesion():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('validaLogin'))

# ================================================
#         FORMULARIO DE DATOS DE SALUD
# ================================================

@app.route("/formSalud")
def formSalud():
    return render_template("datosSalud.html")


@app.route("/guardar_info_salud", methods=["POST"])
def guardar_info_salud():
    if 'usuario_email' not in session:
        flash("Por favor, inicia sesión para actualizar tu información", "error")
        return redirect(url_for('sesion'))

    usuario_id = session['usuario_id']
    altura_cm = request.form['altura_cm']
    peso_actual_kg = request.form['peso_actual_kg']
    peso_objetivo_kg = request.form['peso_objetivo_kg']
    nivel_actividad = request.form['nivel_actividad']
    objetivo_salud = request.form['objetivo_salud']
    meta_semanal = request.form['meta_semanal']
    condiciones_medicas = request.form.get('condiciones_medicas', '')
    medicamentos = request.form.get('medicamentos', '')
    alergias_alimentarias = request.form.get('alergias_alimentarias', '')
    preferencias_sql = ",".join(request.form.getlist('preA'))

    cur = mysql.connection.cursor()

    cur.execute("SELECT id FROM perfiles_usuario WHERE usuario_id=%s", (usuario_id,))
    existe = cur.fetchone()

    if existe:
        cur.execute("""
            UPDATE perfiles_usuario
            SET altura_cm=%s, peso_actual_kg=%s, peso_objetivo_kg=%s,
                nivel_actividad=%s, objetivo_salud=%s, meta_semanal=%s,
                condiciones_medicas=%s, medicamentos=%s, alergias_alimentarias=%s,
                preferencias_alimenticias=%s
            WHERE usuario_id=%s
        """, (
            altura_cm, peso_actual_kg, peso_objetivo_kg,
            nivel_actividad, objetivo_salud, meta_semanal,
            condiciones_medicas, medicamentos, alergias_alimentarias,
            preferencias_sql, usuario_id
        ))
    else:
        cur.execute("""
            INSERT INTO perfiles_usuario (
                usuario_id, altura_cm, peso_actual_kg, peso_objetivo_kg,
                nivel_actividad, objetivo_salud, meta_semanal,
                condiciones_medicas, medicamentos, alergias_alimentarias,
                preferencias_alimenticias
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            usuario_id, altura_cm, peso_actual_kg, peso_objetivo_kg,
            nivel_actividad, objetivo_salud, meta_semanal,
            condiciones_medicas, medicamentos, alergias_alimentarias,
            preferencias_sql
        ))

    mysql.connection.commit()
    cur.close()

    flash("Información de salud guardada correctamente", "success")
    return redirect(url_for('perfil'))


# ================================================
#         CALCULADORAS DE SALUD
# ================================================

@app.route('/calculadoras', methods=['GET', 'POST'])
def calculadoras():
    resultados = {}

    if request.method == 'POST':

        if 'calcular_imc' in request.form:
            peso = float(request.form['peso_imc'])
            altura = float(request.form['altura_imc'])
            resultados["imc"] = f"Tu IMC es: {peso / (altura ** 2):.2f}"

        if 'calcular_tmb' in request.form:
            edad = int(request.form['edad_tmb'])
            peso = float(request.form['peso_tmb'])
            altura = float(request.form['altura_tmb'])
            sexo = request.form['sexo_tmb']
            tmb = 10 * peso + 6.25 * altura - 5 * edad + (5 if sexo == 'hombre' else -161)
            resultados["tmb"] = f"Tu TMB es: {tmb:.2f} kcal/día"

        if 'calcular_gct' in request.form:
            tmb = float(request.form['tmb_gct'])
            actividad = request.form['actividad_gct']
            factores = {'sedentario': 1.2, 'ligera': 1.375, 'moderada': 1.55, 'intensa': 1.725}
            gct = tmb * factores.get(actividad, 1.2)
            resultados["gct"] = f"Tu GCT es: {gct:.2f} kcal/día"

        if 'calcular_peso_ideal' in request.form:
            altura = float(request.form['altura_ideal'])
            if altura < 3:
                altura *= 100
            sexo = request.form['sexo_ideal']
            peso_ideal = altura - 100 - ((altura - 150) / (4 if sexo == 'hombre' else 2))
            resultados["peso_ideal"] = f"Tu peso ideal es: {peso_ideal:.2f} kg"

        if 'calcular_macronutrientes' in request.form:
            gct = float(request.form['gct_macronutrientes'])
            resultados["macros"] = (
                f"Proteínas: {gct * 0.25 / 4:.2f} g, "
                f"Carbohidratos: {gct * 0.45 / 4:.2f} g, "
                f"Grasas: {gct * 0.30 / 9:.2f} g"
            )

    return render_template("calculadoras.html", **resultados)


# ================================================
#                 OTRAS RUTAS
# ================================================

@app.route('/sabermas')
def sabermas():
    return render_template("sabermas.html")


# ================================================
#                 EJECUCIÓN
# ================================================

if __name__ == "__main__":
    app.run(debug=True)
