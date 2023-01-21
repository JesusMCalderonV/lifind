from flask import Flask, render_template, redirect, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash as gen_key
from werkzeug.security import check_password_hash as check_key
from config import ruta, secret_key
from flask_cors import CORS
from flask_mail import Mail, Message
from random import randint

#inicio de la base de datos
db = SQLAlchemy()

#inicio del servidor-aplicaión FLask
app = Flask(__name__)

#Uso de cors para permitir acceso desde las peticiones ajax o fetch
cors = CORS(app)




#Asignamos la dirección a la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{ruta}/database.db'

#Configuración del servicio de correos
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']= 465
app.config['MAIL_USERNAME'] = 'jesusmcalderonv2002@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'jesusmcalderonv2002@gmail.com'
app.config['MAIL_PASSWORD'] = 'eejijulawluqaaqk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

#Asignamos la clave secreta
app.secret_key = secret_key
#Iniciamos la base de datos cuando se cree nuestra aplicación
db.init_app(app)

#En esta sección vamos a crear nuestras tablas de base de datos usando clases de python, con la ayuda del orm (sqlachemy)
#----------------------------------------------------------------
#Definimos la primera tabla que es lade usuario para almacenar cada usuario
#El nombre que le demos a esta clase sera el nombre de nuestra tabla y los atributos serán columnas

#Tabla usuario (User)

#  id  |   username   |   password
#  1   |   jesus_dev  |   python_l
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(16), nullable=False, unique=True)
	password = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=False)

#Tabla de preregistro
class Preregister(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(16), nullable=False, unique=True)
	password = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=False)
	code = db.Column(db.Integer, nullable=False)	

#Tabla Asignatura (Asignature)

#  id  |   name   |   accumulated   |  max_accumulated  |   user 
#  1   | calculo  |      430        |        500        |jesus_dev
class Asignature(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(35), nullable=False, unique=False)
	accumulated = db.Column(db.Float)
	max_accumulated = db.Column(db.Float, nullable = False)
	id_user = db.Column(db.Integer)

#Tabla asignación

#  id  |  work  |   asignature   |    user   |   score  |   score_max
#  1   |  Quiz  |    calculo     | jesus_dev |    15    |     20

class Work(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	work = db.Column(db.String, nullable=False)
	asignature = db.Column(db.String, nullable=None)
	id_user = db.Column(db.Integer)
	score = db.Column(db.Float, nullable=False)
	score_max = db.Column(db.Float, nullable=False)

#----------------------------------------------------------------

@app.route('/')
def index():
	if 'id_user' in session:
		return redirect('/home')
	return render_template('login.html')

@app.route('/add_asignature', methods=['POST', 'GET'])
def add_asignature():
	if request.method == 'POST':
		asignature_clean = request.form['name']
		if asignature_clean[len(asignature_clean)-1] == " ":
			asignature_clean = asignature_clean[:-1]
		asignaturas_user = db.session.query(Asignature).filter_by(id_user=session['id_user']).all()
		if asignaturas_user != None:
			for i in asignaturas_user:
				if i.name == asignature_clean:
					return 'Esta asignatura ya está creado' #redirect('/add_asignature')
		try:
			new_asignature = Asignature(name=asignature_clean, accumulated=0.0, max_accumulated=request.form['max_accumulated'], id_user = session['id_user'])
			db.session.add(new_asignature)
			db.session.commit()
			return f'Registrada de manera exitosa la asignatura {asignature_clean}' #redirect('/add_asignature')
		except:
			return 'Error a la hora de registrar la asignatura'
	return render_template('add_asignature.html')

@app.route('/index')
def home():
	if 'id_user' in session:
		user = db.session.query(User).get(session['id_user'])
		asignatures = db.session.query(Asignature).filter_by(id_user=session['id_user']).all()
		return  render_template('home.html', user = user, asignatures = asignatures, link = 'General')

@app.route('/sign_up')
def sign_up():
	return render_template('register.html')

@app.route('/log_out')
def log_out():
	if 'id_user' in session:
		session.pop('id_user')
	return redirect('/')

@app.route('/login', methods = ['POST'])
def login():
	if request.method == 'POST':
		user = request.form['user']
		password = request.form['password']
		validation = db.session.query(User).filter_by(username=user).first()
		if validation != None:
			print(check_key(validation.password, password))
			if user == validation.username and check_key(validation.password, password) == True:
				session['id_user'] = validation.id
				return redirect('/home')
			else:
				return "Password incorrect"
		return "Eror: The user not exists"

@app.route('/preregistrar', methods=['POST'])
def preregistrar():
	if request.method == 'POST':
		key = gen_key(request.form['password'], 'pbkdf2:sha512:1000', salt_length=8)
		code_gen = randint(1111, 9999)
		print(code_gen)
		if check_key(key, request.form['password']) == True and request.form['password'] != "":
			preregister = Preregister(username=request.form['user'],password= key, email = request.form['email'], code = code_gen)
			try:
				db.session.add(preregister)
				db.session.commit()
				msg = Message(
				subject = "Código de verificación LiFind", recipients=[request.form['email']], html = f"<h2>Codigo LiFind: {code_gen}</h2><br>  <br><p>Se ha hecho el registro en LiFind, tu código de verificación es: {code_gen}. <br>Si no has sido tú asegurate de que tu cuenta esté protegida</p>")
				mail.send(msg)
				return render_template('codigo.html', email = request.form['email'])
			except:
				return "This user is in use."
		else:
			return "Error: an error occurred at the time of registration."
	else:
		return redirect('/sign_up')

@app.route('/registrar', methods=['POST'])
def registrar():
	if request.method == 'POST':
			user_data = db.session.query(Preregister).filter_by(email=request.form['email']).first()
			print(int(request.form['code'])== user_data.code)
			if int(request.form['code']) == user_data.code:
				user = User(username=user_data.username,password= user_data.password, email = request.form['email'])
				try:
					db.session.add(user)
					db.session.query(Preregister).filter_by(email=request.form['email']).delete()
					db.session.commit()
					msg = Message(
					subject = "Registrado exitosamente", recipients=[request.form['email']], html = f"<h2>Te has regitrado de manera exitosa con el usuario {user_data.username}</h2><br>  <br><p>Se ha hecho el registro en LiFind. Te damos la bienvenida a este bonito proyecto. <br>Si no has sido tú asegurate de que tu cuenta esté protegida</p>")
					mail.send(msg)
					return render_template('login.html')
				except:
					return "This user is in use."

			else:
				return render_template('codigo.html', email= request.form['email'])
	else:
		return redirect('/sign_up')

@app.route('/add_work', methods=['POST', 'GET'])
def add_work():
	print(session['id_user'])
	asignatures = db.session.query(Asignature).filter_by(id_user=session['id_user']).all()
	if asignatures != None:
		if request.method == 'POST':
			new_work = Work(work=request.form['work'], asignature=request.form['asignature'], id_user=session['id_user'], score = request.form['score'], score_max=request.form['score_max'])
			try:
				new_max = 0
				db.session.add(new_work)
				db.session.commit()
				works = db.session.query(Work).filter_by(id_user = session['id_user'], asignature=request.form['asignature']).all()
				print(works)
				for i in works:
					print(i.asignature)
					new_max += i.score
				print(new_max)
				asign = db.session.query(Asignature).filter_by(id_user = session['id_user'], name=request.form['asignature']).first()
				db.session.query(Asignature).filter_by(id=asign.id).update({Asignature.accumulated: new_max})
				db.session.commit()
				return 'Tarea registrada'
			except:
				return 'Error al registrar'
		return render_template('add_score.html', asignatures = asignatures)
	return 'No hay materias aún'

@app.route('/asignatures/<string:name>')
def details_asignature(name):
	if 'id_user' in session:
		works = db.session.query(Work).filter_by(id_user = session['id_user'], asignature=name).all()
		return render_template('asignatures.html', works = works, name = name, link = 'asignatures')
	else:
		return "No hay una sesión válida actualmente"

@app.route('/<string:link>')
def renderizar(link):
	return render_template(f'{link}.html', link = link)


@app.route('/api/asi/asignatures')
def get_all_asignatures():
	materias = db.session.query(Asignature).filter_by(id_user=session['id_user']).all()
	materias_list = []
	materias_num = []
	for i in materias:
		materias_list.append(i.name)
		materias_num.append(i.accumulated)
	return jsonify({"materias": materias_list, "puntos": materias_num})


if __name__=='__main__':
	#Le damos la orden de crear todas las tablas definidas si se encuentra la apĺicaión iniciada y la base de datos ciumple con todos las condiciones
	with app.app_context():
		db.create_all()
	app.run(debug=True)