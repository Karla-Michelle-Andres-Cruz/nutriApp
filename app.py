from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TIAMIOSSOTT12'

usuarioR = {}

@app.route('/')
def base():
    return render_template("inicio.html")

@app.route('/ini')
def inicio():
    return render_template("inicio.html")

@app.route('/perfil', methods=['GET'])
def perfil():
    if 'usuario_email' not in session:
        flash("Inicia sesión para ver tu perfil", "error")
        return redirect(url_for('sesion'))

    email = session['usuario_email']
    usuario = usuarioR.get(email, {})
    return render_template('perfilUsuarios.html', usuario=usuario)

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
    peso = float(request.form["peso"])
    altura = float(request.form["altura"])

    if contraseña != conf_contraseña:
        flash("La contraseña no coincide", "error")
        return redirect(url_for("registro"))

    if email in usuarioR:
        flash("Ese correo ya está registrado", "error")
        return redirect(url_for("registro"))

    usuarioR[email] = {
    'nombre': nombre,
    'apellido': apellidos,
    'genero': genero,
    'email': email,
    'peso': peso,
    'altura': altura,
    'contraseña': contraseña,
    'objetivo': request.form.get('objetivo'),
    'restricciones': request.form.get('restricciones'),
    'experiencia': request.form.get('experiencia')
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

if __name__ == "__main__":
    app.run(debug=True)
