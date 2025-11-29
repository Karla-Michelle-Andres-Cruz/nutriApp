from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'TIAMIOSSOTT12'

# Configuración MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'usuarios'


mysql = MySQL(app)

#declaracion de la API
API_BASE = "https://api.nal.usda.gov/fdc/v1/"
API_KEY = "QweiYpuEmJTfQlcfZLdquUSeiCqxe7sGaLQo2OaJ"



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
#               Rutas Principales
# ================================================

@app.route('/')
def base():
    usuario = session.get("usuario_email")
    return render_template("inicio.html", usuario=usuario)

@app.route('/ini')
def inicio():
    usuario = session.get("usuario_email")
    return render_template("inicio.html", usuario=usuario)



# ================================================
#               Perfil de ususario
# ================================================

@app.route('/perfil')
def perfil():
    if 'usuario_email' not in session:
        flash("Inicia sesión para ver tu perfil", "error")
        return redirect(url_for('sesion'))

    usuario_id = session['usuario_id']
    cur = mysql.connection.cursor()

    # Usuario
    cur.execute("SELECT * FROM usuarios WHERE id=%s", (usuario_id,))
    usuario = cur.fetchone()

    # Salud
    cur.execute("SELECT * FROM perfiles_usuario WHERE usuario_id=%s", (usuario_id,))
    salud = cur.fetchone()

    cur.close()

    return render_template("perfilUsuarios.html", usuario=usuario, salud=salud)



# ================================================
#    Editar información del usuario
# ================================================

@app.route('/editarUsuario', methods=['GET', 'POST'])
def editarUsuario():
    if 'usuario_id' not in session:
        flash("Inicia sesión para editar tu información", "error")
        return redirect(url_for('sesion'))

    usuario_id = session['usuario_id']
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        paterno = request.form['paterno']
        materno = request.form['materno']
        genero = request.form['genero']
        telefono = request.form['telefono']
        fecha_nacimiento = request.form['fecha_nacimiento']

        cur.execute("""
            UPDATE usuarios 
            SET nombre=%s, paterno=%s, materno=%s, 
                genero=%s, telefono=%s, fecha_nacimiento=%s 
            WHERE id=%s
        """, (nombre, paterno, materno, genero, telefono, fecha_nacimiento, usuario_id))

        mysql.connection.commit()
        cur.close()

        flash("Información actualizada correctamente", "success")
        return redirect(url_for('perfil'))

    # Obtener datos actuales
    cur.execute("SELECT * FROM usuarios WHERE id=%s", (usuario_id,))
    usuario = cur.fetchone()
    cur.close()

    return render_template("editarUsuario.html", usuario=usuario)


# ================================================
#               Registro usuarios
# ================================================


#manda la fecha a el formulario registro 
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
    fecha_nacimiento = request.form['fecha_nacimiento']
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

        #inserta los datos a la base de datos 'usuario'
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
#                   inicio sesion
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

            # usuario[1] = email, usuario[2] = password, ususario[0] = id
            if check_password_hash(usuario[2], password):
                session['usuario_id'] = usuario[0]
                session['usuario_nombre'] = usuario[3]
                session['usuario_email'] = usuario[1]

                #mensaje de bienvenida con el nombre del usuario
                flash(f'¡Bienvenido {usuario[3]}!', 'success')
                return redirect(url_for('inicio'))
            else:
                flash('Contraseña incorrecta', 'danger')
                return render_template('sesion.html')
        else:
            flash('El correo no esta registrado', 'danger')
            return render_template('sesion.html')




@app.route("/cerrarsesion")
def cerrarsesion():
    session.clear()
    flash("Has cerrado sesión exitosamente", "success")
    return redirect(url_for("inicio"))

# ================================================
#         Formulario de datos de salud
# ================================================

@app.route("/formSalud")
def formSalud():
    return render_template("datosSalud.html")


@app.route("/guardar_info_salud", methods=["POST"])
def guardar_info_salud():

    #si no hay usuario no te dejara actualizar los datos de salud y/o guardarlos
    if 'usuario_email' not in session:
        flash("Por favor, inicia sesión para actualizar tu información", "error")
        return redirect(url_for('sesion'))

    #toma los datos del formuario de salud y los guarda
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
    preferencias_alimentarias = request.form.get('preferencias_alimentarias', '')

    cur = mysql.connection.cursor()

    #se sincroniza con la tabla 'usuario' usando la llave foranea 'usuario_id
    cur.execute("SELECT id FROM perfiles_usuario WHERE usuario_id=%s", (usuario_id,))
    existe = cur.fetchone()

    #si exite ya un registro de datos de salud y el usuario vuelve a cambiar los datos se ejecuta un Update
    if existe:
        cur.execute('UPDATE perfiles_usuario SET altura_cm=%s, peso_actual_kg=%s, peso_objetivo_kg=%s, nivel_actividad=%s, objetivo_salud=%s, meta_semanal=%s, condiciones_medicas=%s, medicamentos=%s,  alergias_alimentarias=%s,preferencias_alimentarias=%s WHERE usuario_id=%s', 
                    (altura_cm, peso_actual_kg, peso_objetivo_kg, nivel_actividad, objetivo_salud, meta_semanal, condiciones_medicas, medicamentos, alergias_alimentarias, preferencias_alimentarias, usuario_id)
        )
        #si no existe un regiestro previo entonces se inserta los datos del formulario de salud
    else:
        cur.execute('INSERT INTO perfiles_usuario (usuario_id, altura_cm, peso_actual_kg, peso_objetivo_kg, nivel_actividad, objetivo_salud, meta_semanal,condiciones_medicas, medicamentos, alergias_alimentarias, preferencias_alimentarias) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                    (usuario_id, altura_cm, peso_actual_kg, peso_objetivo_kg, nivel_actividad, objetivo_salud, meta_semanal, condiciones_medicas, medicamentos, alergias_alimentarias, preferencias_alimentarias)
        )

    mysql.connection.commit()
    cur.close()

    flash("Información de salud guardada correctamente", "success")
    return redirect(url_for('perfil'))


# ================================================
#         Calculadoras
# ================================================

@app.route('/calculadoras')
def calculadoras():
    return render_template("calculadoras.html")


@app.route('/calcularImc', methods=['GET', 'POST'])
def calcularImc():
    resultado = None
    clasificacion = None

    if request.method == 'POST':
        peso = float(request.form['peso'])
        altura = float(request.form['altura'])
        imc = peso / (altura**2)

        # Resultado numérico
        resultado = f"Tu IMC es: {imc:.2f}"

        # Clasificación IMC
        if imc < 18.5:
            clasificacion = "Bajo peso"
        elif 18.5 <= imc < 25:
            clasificacion = "Peso normal"
        elif 25 <= imc < 30:
            clasificacion = "Sobrepeso"
        elif 30 <= imc < 35:
            clasificacion = "Obesidad grado I"
        elif 35 <= imc < 40:
            clasificacion = "Obesidad grado II"
        else:
            clasificacion = "Obesidad grado III"

    return render_template("caImc.html",
                            resultado=resultado,
                            clasificacion=clasificacion)


@app.route('/calcularTmb', methods=['GET', 'POST'])
def calcularTmb():
    resultado = None

    if request.method == 'POST':
        edad = int(request.form['edad'])
        peso = float(request.form['peso'])
        altura = float(request.form['altura'])
        sexo = request.form['sexo']

        if sexo == 'hombre':
            tmb = 10*peso + 6.25*altura - 5*edad + 5
        else:
            tmb = 10*peso + 6.25*altura - 5*edad - 161

        resultado = f"Tu TMB es: {tmb:.2f} kcal/día"

    return render_template("calTmb.html", resultado=resultado)


@app.route('/calcularGct', methods=['GET', 'POST'])
def calcularGct():
    resultado = None

    if request.method == 'POST':
        tmb = float(request.form['tmb'])
        actividad = request.form['actividad']

        factores = {
            'sedentario': 1.2,
            'ligera': 1.375,
            'moderada': 1.55,
            'intensa': 1.725
        }

        gct = tmb * factores[actividad]
        resultado = f"Tu GCT es: {gct:.2f} kcal/día"

    return render_template("calGct.html", resultado=resultado)


@app.route('/calcularPesoIdeal', methods=['GET', 'POST'])
def calcularPesoIdeal():
    resultado = None

    if request.method == 'POST':
        altura = float(request.form['altura'])
        if altura < 3:
            altura *= 100

        sexo = request.form['sexo']

        if sexo == 'hombre':
            peso_ideal = altura - 100 - ((altura-150)/4)
        else:
            peso_ideal = altura - 100 - ((altura-150)/2)

        resultado = f"Tu peso ideal es: {peso_ideal:.2f} kg"

    return render_template("calPesoI.html", resultado=resultado)


@app.route('/calcularMacronutrientes', methods=['GET', 'POST'])
def calcularMacronutrientes():
    resultado = None

    if request.method == 'POST':
        gct = float(request.form['gct'])
        prote = gct*0.25/4
        carbo = gct*0.45/4
        grasas = gct*0.30/9

        resultado = f"Proteínas: {prote:.2f} g – Carbohidratos: {carbo:.2f} g – Grasas: {grasas:.2f} g"

    return render_template("calMacro.html", resultado=resultado)


# ================================================
#                 Otras rutas
# ================================================

@app.route('/sabermas')
def sabermas():
    return render_template("sabermas.html")

# ================================================
#               Busacador de alimentos
# ================================================

@app.route("/buscar_alimentos")
def buscar_alimentos():
    return render_template("recetas.html")


@app.route("/search", methods=["POST"])
def buscar_alimento():
    comNombre = request.form.get("food_name", "").strip().lower()

    if not comNombre:
        flash("Por favor, ingresa el nombre de un alimento.", "error")
        return redirect(url_for("buscar_alimentos"))

    try:
        buscaUrl = f"{API_BASE}foods/search?query={comNombre}&api_key={API_KEY}"
        busResponse = requests.get(buscaUrl)

        if busResponse.status_code != 200:
            flash("No se pudo conectar con la API del USDA.", "error")
            return redirect(url_for("buscar_alimentos"))

        busData = busResponse.json()

        if "foods" not in busData or len(busData["foods"]) == 0:
            flash(f'No se encontraron resultados para "{comNombre}".', "error")
            return redirect(url_for("buscar_alimentos"))

        comida = busData["foods"][0]
        fdc_id = comida["fdcId"]

        detUrl = f"{API_BASE}food/{fdc_id}?api_key={API_KEY}"
        detResponse = requests.get(detUrl)
        detData = detResponse.json()

        food_info = {
            "description": detData.get("description", "Sin descripción"),
            "fdcId": detData.get("fdcId"),
            "nutrientes": [
                {
                    "name": n.get("nutrientName", ""),
                    "amount": n.get("value"),
                    "unit": n.get("unitName", "")
                }
                for n in detData.get("foodNutrients", [])
            ]
        }

        return render_template("resultado.html", food=food_info)

    except requests.exceptions.RequestException:
        flash("Error al conectar con la API del USDA. Intenta de nuevo más tarde.", "error")
        return redirect(url_for("buscar_alimentos"))


if __name__ == "__main__":
    app.run(debug=True)
