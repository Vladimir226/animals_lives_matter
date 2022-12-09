from flask import Flask, render_template, request, g, redirect, url_for, flash
from flask_login import LoginManager, login_user
import os
import sqlite3

from werkzeug.security import check_password_hash

from db import *
from UserLogin import UserLogin

#configurate
DATABASE = '/tmp/app.db'
DEBUG = True
SECRET_KEY = 'vovan'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'app.db')))

# login_manager = LoginManager(app)




database = ALM("postgres", "123456", "localhost", "5432")

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_phone):
    print("loader user")
    return UserLogin().fromDB(user_phone, database)

@app.teardown_appcontext
def closw_db(error):
    if hasattr(g,'link_db'):
        g.link_db.close()

doctors = []
doctor_0 = {  
    'id': 0,
    'full_name': 'Афанасий Владимир Алексеевич',
    'phone': '79991382501',
    'specialization': 'хирург',
    'about': 'Много непонятного текста, который не несет никакого смысла и существует лишь для того, чтобы быть тут',
    'url_photo': '',
    'count_admissions': 123
}
doctors.append(doctor_0)

@app.route('/profile', methods=['GET','POST'])
def profile():
    # db= get_db()
    return render_template("profile.html",doctor = doctors[0])

@app.route('/admissions_history')
def admissions_history():
    return render_template("admissions_history.html")

@app.route('/add_admission')
def add_admission():
    return render_template('add_admission.html')
import db

@app.route('/edit_profile')
def edit_profile():
    return render_template('edit_profile.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = database.get_doctor(request.form['login'])
        if user and check_password_hash(user['password'], request.form['password']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('profile'))

    flash('Неверная пара логин/пароль', 'error')

    return render_template('login.html', title='Авторизация')

@app.route('/')
def alm_library():
    return render_template('alm_library.html', persons = database.get_all_clients())

@app.route('/animals/<int:phone_number>')
def alm_animals(phone_number):
    return render_template('alm_animals.html', animals = database.get_animals(phone_number))

@app.route('/admissions/<int:animal_id>')
def admissions(animal_id):
    return render_template('admissions.html', receptions = database.get_animal_receptions(animal_id))

@app.route('/admission/<int:reception_id>')
def admission(reception_id):
    return render_template("admission.html", info = database.get_reception(reception_id))


if __name__ =="__main__":
    app.run(debug=True)