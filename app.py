from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TIAMIOSSOTT12'


@app.route('/')
def base():
    return render_template("inicio.html")


@app.route('/ini')
def inicio():
    return render_template("inicio.html")

@app.route("/registro")
def registro():
    dias = list(range(1, 32))
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio","Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    año_actual = datetime.now().year
    años = list(range(año_actual, 1905, -1))
    return render_template("registro.html", dias=dias, meses=meses, años=años)


@app.route("/iniciosesion")
def sesion():
    if session.get('logueado'):
        return redirect(url_for("index"))
    return render_template("sesion.html")

@app.route("/validalogin", methods=['POST'])
def validaLogin():
    if request.method == "POST":
        email = request.form.get('email', '').strip()
        contraseña = request.form.get('contraseña', '')
        
        if not email or not contraseña:
            flash('Por favor ingresa email y contraseña', 'error')
            return redirect(url_for('sesion'))
        
        if email in usuariosRegist:
            usuario = usuariosRegist[email]
            if usuario['contraseña'] == contraseña:
                session['usuario_email'] = email
                session['usuario'] = usuario['nombre']
                session['logueado'] = True
                flash(f"Bienvenido {usuario['nombre']}", "success")
                return redirect(url_for("index"))
            else:
                flash('Contraseña incorrecta', 'error')
        else:
            flash('Usuario no encontrado', 'error')
        
        return redirect(url_for('sesion'))

@app.route("/cerrarsesion")
def cerrarsesion():
    session.clear()
    flash("Has cerrado sesión exitosamente", "success")
    return redirect(url_for("index"))




if __name__ == "__main__":
    app.run(debug=True)