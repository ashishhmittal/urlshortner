from flask import Flask, render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, BooleanField, SubmitField, validators
from pymongo import MongoClient
from wtforms.validators import InputRequired, Length
import random

name = ''
rand = ''

app = Flask(__name__)
app.config['SECRET_KEY']= 'NotMe'
client = MongoClient("mongodb://bizzle:Shriramg1@ds221003.mlab.com:21003/urlshortener")
db = client['urlshortener']
users = db.users

class LoginForm(FlaskForm):
    username = TextField('username', validators=[InputRequired()])
    email = TextField('Email Address', [validators.Required()])
    password = PasswordField('Password',[validators.Required()])
    urls = TextField('urls', validators=[InputRequired()])



@app.route('/', methods=['POST','GET'])
def index():    
	form = LoginForm()
	users = db.users
	msg = ''
	if request.method == 'POST':
		search = users.find_one({'username':form.username.data})
		if search:
			msg = 'Username already exists'
		else:
			users.insert({'username':form.username.data,'password':form.password.data,'email':form.email.data})
			return redirect(url_for('login'))

	return render_template('signup.html', form=form, msg=msg)

@app.route('/login/', methods=['POST','GET'])
def login():
	form = LoginForm()
	users = db.users
	session['username'] = None
	msg = 'Invalid Username or Password'
	if request.method == 'POST':
		search = users.find_one({'username':form.username.data})
		if search is None:
			return render_template('index.html', msg=msg, form=form)
			
		authu = search['username']
		authp = search['password']
		if authu == form.username.data and authp == form.password.data:
			session['username'] = form.username.data
			return redirect(url_for('url', name=authu))
		
		return render_template('index.html', msg=msg, form=form)

	return render_template('index.html', form=form)

@app.route('/<name>', methods=['POST','GET'])
def url(name):
	form = LoginForm()
	urls = db[name]
	msg = None
	if session['username']:
		if request.method == 'POST':
			search = urls.find_one({'real':form.urls.data})
			if search:
				msg = 'URL already shortned'
				return redirect(url_for('url', name=name))
			else:
				rand = random.randint(0, pow(10, 5))
				temp = "http://127.0.0.1:5000/"+name+"/"+ str(rand)
				urls.insert({'real':form.urls.data,'short':temp})
				return redirect(url_for('url', name=name))

		else:
			hi = urls.find()
			return render_template('shortner.html', form=form, name=name, hi=hi)

	return redirect(url_for('login'))


@app.route('/<name>/<trunc>', methods=['POST','GET'])
def link(name,trunc): 
	urls = db[name]
	search = urls.find_one({'short':'http://127.0.0.1:5000/'+name+'/'+trunc})
	if search:
		return redirect(search['real'])
	return redirect(url_for('url', name=name))

@app.route('/logout')
def logout():
	session['username'] = None
	return redirect(url_for('login'))


if __name__ == '__main__':
	app.secret_key= 'TheMainFile'
	app.run(debug=True)
