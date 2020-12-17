from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from db import get_db, close_db
import os
from werkzeug.security import generate_password_hash,check_password_hash
import utils
import yagmail as yagmail
UPLOAD_FOLDER= os.path.abspath("./static/images/")
#from OpenSSL, crypto import FILETYPE_PEM
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["UPLOAD_FOLDER"]= UPLOAD_FOLDER

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



            user = db.execute('SELECT * FROM usuarios WHERE usuario=?',(username,)).fetchone()

            
            if user is None:
                error="Usuario o contraseña invalidos"
                flash(error)
            
            else:
                if check_password_hash(user[1],password):

                #Es admin
                    if user[3]== 1:
                        return redirect(url_for('admin'))
                
                    return redirect(url_for('store'))
            return render_template('login.html')
        return render_template('login.html')
    except TypeError as e:
        print("Ocurrio un error ",e)
        return render_template('login.html')

@app.route('/store/')
def store():
    close_db()
    db = get_db()
    data = db.execute('SELECT * FROM productos').fetchall()

    return render_template('store.html', products = data)

@app.route('/admin/editProduct/<id_producto>/')
def updateProductadmin(id_producto):
    close_db()
    db=get_db()
    productdata = db.execute('SELECT * FROM productos WHERE id_producto = {0}'.format(id_producto)).fetchall()

    return render_template('editProductadmin.html', product = productdata[0])

@app.route('/store/editProduct/<id_producto>/')
def updateProductstore(id_producto):
    close_db()
    db=get_db()
    productdata = db.execute('SELECT * FROM productos WHERE id_producto = {0}'.format(id_producto)).fetchall()

    return render_template('editProductstore.html', product = productdata[0])

@app.route('/admin/updateProduct/<id_producto>/', methods=('GET','POST'))
def updateproductadmin(id_producto):

    if request.method == 'POST':
        nombreprod = request.form['np']
        descripcionprod = request.form['dp']
        cantidadprod = request.form['cp']
        close_db()
        db = get_db()
        db.execute('UPDATE productos SET nombre = ?, descripcion = ?, cantidad = ? WHERE id_producto = ?',(nombreprod,descripcionprod,cantidadprod, id_producto))
        db.commit()
        return redirect(url_for('admin'))
    error = "Error actualizando producto"
    flash(error)
    return redirect(url_for('editProduct'))

@app.route('/store/updateProduct/<id_producto>/', methods=('GET','POST'))
def updateproductstore(id_producto):

    if request.method == 'POST':
        nombreprod = request.form['np']
        descripcionprod = request.form['dp']
        cantidadprod = request.form['cp']
        close_db()
        db = get_db()
        db.execute('UPDATE productos SET nombre = ?, descripcion = ?, cantidad = ? WHERE id_producto = ?',(nombreprod,descripcionprod,cantidadprod, id_producto))
        db.commit()
        return redirect(url_for('store'))
    error = "Error actualizando producto"
    flash(error)
    return redirect(url_for('editProduct'))

@app.route('/deleteProduct/<string:id_producto>/')
def deleteProduct(id_producto):
    close_db()
    db = get_db()
    db.execute('DELETE FROM productos WHERE id_producto = {0}'.format(id_producto))
    db.commit()
    return redirect(url_for('admin'))

@app.route('/admin/')
def admin():
    db = get_db()
    data = db.execute('SELECT * FROM productos').fetchall()
    #print(data)
    return render_template('admin.html',products = data)

@app.route('/registerProduct/',methods=('GET','POST'))
def registerProduct():
    try:
        if request.method == 'POST':
            db=get_db()
            nombre= request.form['np']
            descripcion= request.form['dp']
            cantidad= request.form['cp']
            f = request.files['imagenp']

            filename= f.filename
            
            if db.execute('SELECT * FROM productos WHERE nombre=?',(nombre,)).fetchone() is not None:
                error= "El nombre del producto ya esta registrado"
                flash(error)
                return render_template('registerProduct.html')

            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            send_from_directory(app.config['UPLOAD_FOLDER'],filename)
            db.execute('INSERT INTO productos (nombre,descripcion,cantidad, imagen) VALUES (?,?,?,?)',(nombre,descripcion,cantidad,"../static/images/"+filename+"/"))
            db.commit()
            
            return redirect(url_for('admin'))
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
        print("Ocurrio un eror:", e)
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
        print("Ocurrio un eror:", e)
        return render_template('login.html')

if __name__ == '__main__':
    app.run()