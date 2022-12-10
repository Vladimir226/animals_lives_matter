from flask import Flask, render_template, request, g, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
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
login_manager.login_view = 'login'
# login_manager.login_message = 'Авторизуйтесь для доступа к закрытым сессия'
# login_manager.login_message_category = 'success'
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

@app.before_request
def before_request():
     g.auth = current_user.is_authenticated
     print(current_user.is_authenticated)

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    # db= get_db()
    return render_template("profile.html",doctor = database.get_doctor(current_user.get_id()))

@app.route('/admissions_history')
@login_required
def admissions_history():
    return render_template("admissions_history.html")

@app.route('/add_admission')
@login_required
def add_admission():
    return render_template('add_admission.html')
import db

@app.route('/edit_profile')
@login_required
def edit_profile():
    return render_template('edit_profile.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        user = database.get_doctor(request.form['login'])
        if user and check_password_hash(user['password'], request.form['password']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('profile'))

    flash('Неверная пара логин/пароль', 'error')

    return render_template('login.html', title='Авторизация')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('alm_library'))

@app.route('/')
@login_required
def alm_library():
    return render_template('alm_library.html', persons = database.get_all_clients())

@app.route('/animals/<int:phone_number>')
@login_required
def alm_animals(phone_number):
    return render_template('alm_animals.html', animals = database.get_animals(phone_number))

@app.route('/admissions/<int:animal_id>')
@login_required
def admissions(animal_id):
    return render_template('admissions.html', receptions = database.get_animal_receptions(animal_id))

@app.route('/admission/<int:reception_id>')
@login_required
def admission(reception_id):
    return render_template("admission.html", info = database.get_reception(reception_id))

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    if request.method == 'POST':
        # вот тут надо вызвать селекты и в persons закинуть результат поиска
        searcher = request.form['search']
        return redirect(url_for('search_result', persons = ...))

    return render_template("search.html")

@app.route('/search/result')
@login_required
def search_result():
    return render_template("search_result.html")

if __name__ =="__main__":
    app.run(debug=True)