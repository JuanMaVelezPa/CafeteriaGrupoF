from flask import Flask, render_template, request, flash

import utils
import os 
import yagmail as yagmail
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def hello_world():
    return render_template('login.html')

@app.route('/home/')
def myHome():
    return render_template('store.html')

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/store/')
def store():
    return render_template('store.html')

@app.route('/admin/')
def admin():
    return render_template('admin.html')

@app.route('/registerProduct/')
def registerProduct():
    return render_template('registerProduct.html')

@app.route('/passwordLost/')
def passwordLost():
    return render_template('passwordLost.html')



@app.route('/register/', methods=('GET','POST'))
def register():
    try:
        if request.method == 'POST':
            username = request.form['usuario']
            password = request.form['password']
            email = request.form['email']
            error = None

            if not utils.isUsernameValid(username):
                error = "El usuario debe ser alfanumerico"
                flash(error)
                return render_template('register.html')

            if not utils.isEmailValid(email):
                error = 'Correo inválido'
                flash(error)
                return render_template('register.html')

            if not utils.isPasswordValid(password):
                error = 'La contraseña debe tener por los menos una mayúcscula y una mínuscula y 8 caracteres'
                flash(error)
                return render_template('register.html')

            serverEmail = yagmail.SMTP('CafeteriaAromaMisionTic@gmail.com', 'Maracuya123')

            serverEmail.send(to=email, subject='Activa tu cuenta '+username+" en Cafeteria Aroma",
                             contents='Bienvenido, usa este link para activar tu cuenta')

            flash('Revisa tu correo para activar tu cuenta')

            return render_template('login.html')

        return render_template('register.html')
    except Exception as e:
        #print("Ocurrio un eror:", e)
        return render_template('register.html')

@app.route('/passwordLost/', methods=('GET','POST'))
def revision():
    try:
        if request.method == 'POST':
            username = request.form['usuario']
            password = request.form['password']
            reviewPassword = request.form['reviewPassword']
            email = request.form['email']
            error = None

            if not utils.isUsernameValid(username):
                error = "El usuario debe ser alfanumerico"
                flash(error)
                return render_template('passwordLost.html')

            if not utils.isEmailValid(email):
                error = 'Correo inválido'
                flash(error)
                return render_template('passwordLost.html')

            if not utils.isPasswordValid(password):
                error = 'La contraseña debe tener por los menos una mayúcscula y una mínuscula y 8 caracteres'
                flash(error)
                return render_template('passwordLost.html')

            if not utils.isPasswordValid(reviewPassword):
                error = 'La contraseña debe tener por los menos una mayúcscula y una mínuscula y 8 caracteres'
                flash(error)
                return render_template('passwordLost.html')

            if not (password == reviewPassword):
                error = 'Las contraseñas ingresadas no coinciden'
                flash(error)
                return render_template('passwordLost.html')

            serverEmail = yagmail.SMTP('CafeteriaAromaMisionTic@gmail.com', 'Maracuya123')

            serverEmail.send(to=email, subject='Cambio Contraseña '+username+" en Cafeteria Aroma",
                             contents='El cambio de la contraseña fue Exitoso XD \n\n'+"**Su contraseña nueva es: "+password)

            flash('Revisa tu correo la confirmación de nueva constraseña')

            return render_template('login.html')

        return render_template('login.html')
    except Exception as e:
        #print("Ocurrio un eror:", e)
        return render_template('login.html')

if __name__ == '__main__':
    app.run()