from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TIAMIOSSOTT12'


@app.route('/')
def base():
    return render_template("inicio.html")


@app.route('/ini')
def inicio():
    return render_template("inicio.html")




if __name__ == "__main__":
    app.run(debug=True)