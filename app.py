from flask import Flask, render_template, request, flash
from db import get_db, close_db
from werkzeug.security import generate_password_hash,check_password_hash

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

@app.route('/login/', methods=('GET','POST'))
def login():
    try: 
        if request.method == 'POST':
            db = get_db()
            username = request.form['username']
            password = request.form['password']

            if not username:
                error= "Debes ingresar el usuario"
                flash(error)
                return render_template('login.html')
            if not password:
                error= "Contraseña requerida"
                flash(error)
                return render_template('login.html')

            print("usuario: "+username+" contraseña: "+password)

            user = db.execute('SELECT * FROM usuarios WHERE usuario=?',(username,)).fetchone()
            print(user)
            
            if user is None:
                error="Usuario o contraseña invalidos"
                flash(error)
            
            else:
                if check_password_hash(user[1],password):

                #Es admin
                    if user[3]== 1:
                        return render_template('admin.html')
                
                    return render_template('store.html')
            return render_template('login.html')
        return render_template('login.html')
    except TypeError as e:
        print("Ocurrio un error ",e)
        return render_template('login.html')

@app.route('/store/')
def store():
    return render_template('store.html')

@app.route('/admin/')
def admin():
    return render_template('admin.html')

@app.route('/registerProduct/',methods=('GET','POST'))
def registerProduct():
    try:
        if request.method == 'POST':
            db=get_db()
            nombre= request.form['np']
            descripcion= request.form['dp']
            cantidad= request.form['cp']
            #imagen= request.form['imagenp']
            #print(imagen)
            if db.execute('SELECT * FROM productos WHERE nombre=?',(nombre,)).fetchone() is not None:
                error= "El nombre del producto ya esta registrado"
                flash(error)
                return render_template('registerProduct.html')
            
            db.execute('INSERT INTO productos (nombre,descripcion,cantidad) VALUES (?,?,?)',(nombre,descripcion,cantidad))
            db.commit()
            
            return render_template('admin.html')
        return render_template('registerProduct.html')
    except TypeError as e:
        print("Ocurrio un error ",e)
        return render_template('registerProduct.html')

    

@app.route('/passwordLost/')
def passwordLost():
    return render_template('passwordLost.html')



@app.route('/register/', methods=('GET','POST'))
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            rol = request.form['rol']
            error = None
            db= get_db()

            print(rol)

            db = get_db()

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

            if db.execute('SELECT * FROM usuarios WHERE usuario=? OR correo=?',(username,email)).fetchone() is not None:
                error= "El usuario o correo electronico ya estan registrados"
                flash(error)
                return render_template('register.html')
            hash_password= generate_password_hash(password)
            db.execute('INSERT INTO usuarios (usuario,contraseña,correo,rol,activo) VALUES (?,?,?,?,1)',(username,hash_password,email,rol))
            db.commit()


            serverEmail = yagmail.SMTP('CafeteriaAromaMisionTic@gmail.com', 'Maracuya123')

            serverEmail.send(to=email, subject='Tu cuenta '+username+" en Cafeteria Aroma ha sido creada",
                             contents='Bienvenido')

            flash('Revisa tu correo ')

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