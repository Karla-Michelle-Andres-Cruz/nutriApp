from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from  werkzeug.security import generate_password_hash
from datetime import datetime
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TIAMIOSSOTT12'


# bases de datos /(diccionarios)
usuario2 = {} # usuarios salud registro inicio
usuarioR = {} # info de registrados

@app.route('/')
def base():
    usuario = session.get("usuario_email")
    return render_template("inicio.html", usuario=usuario)

@app.route('/ini')
def inicio():
    usuario = session.get("usuario_email")
    return render_template("inicio.html", usuario=usuario)

# si no hay sesion te devuelve al login
@app.route('/perfil', methods=['GET'])
def perfil():
    if 'usuario_email' not in session:
        flash("Inicia sesión para ver tu perfil", "error")
        return redirect(url_for('sesion'))


# obtiene datos de salud y registro
    email = session['usuario_email']
    usuario = usuarioR.get(email, {})
    salud = usuario2.get(email, {}) 

    return render_template('perfilUsuarios.html', usuario=usuario, salud=salud) #envia los datos al html de perfil u


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
    apellidos = request.form["apellido"]
    genero = request.form["genero"]
    email = request.form["email"]
    contraseña = request.form["contraseña"]
    conf_contraseña = request.form["confirmaContraseña"]

    if contraseña != conf_contraseña:
        flash("La contraseña no coincide", "error")
        return redirect(url_for("registro"))

    if email in usuarioR:
        flash("Ese correo ya está registrado", "error")
        return redirect(url_for("registro"))

#guarda la info en el diccionario
    usuarioR[email] = {
    'nombre': nombre,
    'apellido': apellidos,
    'genero': genero,
    'email': email,
    'contraseña': contraseña
}


    flash(f"¡Registro exitoso para {nombre}!", "success")
    return redirect(url_for("sesion"))

@app.route("/iniciosesion")
def sesion():
    if session.get('logueado'):
        return redirect(url_for("inicio"))
    return render_template("sesion.html")

@app.route("/validalogin", methods=['POST'])
def validaLogin():
    #Toma datos de
    email = request.form.get('email', '').strip()
    contraseña = request.form.get('contraseña', '')

    if not email or not contraseña:
        flash('Por favor ingresa email y contraseña', 'error')
        return redirect(url_for('sesion'))
    
    if email in usuarioR:
        usuario = usuarioR[email]
        if usuario['contraseña'] == contraseña:
            session['usuario_email'] = email
            session['usuario'] = usuario['nombre']
            session['logueado'] = True
            flash(f"Bienvenido {usuario['nombre']}", "success")
            return redirect(url_for("inicio"))
        else:
            flash('Contraseña incorrecta', 'error')
    else:
        flash('Usuario no encontrado', 'error')
    
    return redirect(url_for('sesion'))

@app.route("/cerrarsesion")
def cerrarsesion():
    session.clear()
    flash("Has cerrado sesión exitosamente", "success")
    return redirect(url_for("inicio"))

@app.route("/formSalud")
def formSalud():
    return render_template("datosSalud.html")

@app.route("/guardar_info_salud", methods=["POST"])
def guardar_info_salud():
    if 'usuario_email' not in session:
        flash("Por favor, inicia sesión para actualizar tu información", "error")
        return redirect(url_for('sesion'))

    email = session['usuario_email']

    altura_cm = float(request.form['altura_cm'])
    peso_actual_kg = float(request.form['peso_actual_kg'])
    peso_objetivo_kg = float(request.form['peso_objetivo_kg'])
    nivel_actividad = request.form['nivel_actividad']
    objetivo_salud = request.form['objetivo_salud']
    meta_semanal = request.form['meta_semanal']
    condiciones_medicas = request.form.get('condiciones_medicas', '')
    medicamentos = request.form.get('medicamentos', '')
    alergias_alimentarias = request.form.get('alergias_alimentarias', '')
    preA = request.form.getlist('preA')

    usuario2[email] = {
        'altura_cm': altura_cm,
        'peso_actual_kg': peso_actual_kg,
        'peso_objetivo_kg': peso_objetivo_kg,
        'nivel_actividad': nivel_actividad,
        'objetivo_salud': objetivo_salud,
        'meta_semanal': meta_semanal,
        'condiciones_medicas': condiciones_medicas,
        'medicamentos': medicamentos,
        'alergias_alimentarias': alergias_alimentarias,
        'preA': preA
    }

    flash("Información de salud actualizada con éxito", "success")
    return redirect(url_for('perfil'))


@app.route('/calculadoras', methods=['GET', 'POST'])
def calculadoras():
    imc_resultado = None
    tmb_resultado = None
    gct_resultado = None
    peso_ideal_resultado = None
    macronutrientes_resultado = None

    if request.method == 'POST':
        if 'calcular_imc' in request.form:
            peso = float(request.form['peso_imc'])
            altura = float(request.form['altura_imc'])
            imc = peso / (altura ** 2)
            imc_resultado = f"Tu IMC es: {imc:.2f}"

        if 'calcular_tmb' in request.form:
            edad = int(request.form['edad_tmb'])
            peso = float(request.form['peso_tmb'])
            altura = float(request.form['altura_tmb'])
            sexo = request.form['sexo_tmb']
            if sexo == 'hombre':
                tmb = 10 * peso + 6.25 * altura - 5 * edad + 5
            else:
                tmb = 10 * peso + 6.25 * altura - 5 * edad - 161
            tmb_resultado = f"Tu TMB es: {tmb:.2f} kcal/día"

        if 'calcular_gct' in request.form:
            tmb = float(request.form['tmb_gct'])
            actividad = request.form['actividad_gct']
            if actividad == 'sedentario':
                gct = tmb * 1.2
            elif actividad == 'ligera':
                gct = tmb * 1.375
            elif actividad == 'moderada':
                gct = tmb * 1.55
            elif actividad == 'intensa':
                gct = tmb * 1.725
            gct_resultado = f"Tu GCT es: {gct:.2f} kcal/día"

        if 'calcular_peso_ideal' in request.form:
            altura = float(request.form['altura_ideal'])
            if altura < 3:
                altura *= 100

            sexo = request.form['sexo_ideal']
            if sexo == 'hombre':
                peso_ideal = altura - 100 - ((altura - 150) / 4)
            else:
                peso_ideal = altura - 100 - ((altura - 150) / 2)
            peso_ideal_resultado = f"Tu peso ideal es: {peso_ideal:.2f} kg"

        if 'calcular_macronutrientes' in request.form:
            gct = float(request.form['gct_macronutrientes'])
            proteinas = gct * 0.25 / 4
            carbohidratos = gct * 0.45 / 4
            grasas = gct * 0.30 / 9
            macronutrientes_resultado = f"Proteínas: {proteinas:.2f} g, Carbohidratos: {carbohidratos:.2f} g, Grasas: {grasas:.2f} g"

    return render_template("calculadoras.html", 
                            imc_resultado=imc_resultado,
                            tmb_resultado=tmb_resultado,
                            gct_resultado=gct_resultado,
                            peso_ideal_resultado=peso_ideal_resultado,
                            macronutrientes_resultado=macronutrientes_resultado)
    
    
@app.route('/sabermas')
def sabermas():
    return render_template("sabermas.html")


if __name__ == "__main__":
    app.run(debug=True)
