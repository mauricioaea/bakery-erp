import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Usuario
from werkzeug.security import generate_password_hash, check_password_hash

# Obtener la ruta base del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Configurar la base de datos en la carpeta principal
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'panaderia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta_muy_segura_panaderia_2025'

db.init_app(app)

# Crear las tablas y un usuario admin por defecto
with app.app_context():
    db.create_all()
    # Verificar si ya existe un usuario admin
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        hashed_password = generate_password_hash('admin123')
        admin_user = Usuario(username='admin', password_hash=hashed_password, rol='admin')
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Usuario admin creado: usuario: admin, contraseña: admin123")
    print("✅ Base de datos lista!")
    print(f"📁 Ubicación de la BD: {os.path.join(basedir, 'panaderia.db')}")

# Ruta para el login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['rol'] = user.rol
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

# Ruta para el dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)