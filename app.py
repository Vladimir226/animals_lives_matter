from flask import Flask, render_template, request, g, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import sqlite3

from werkzeug.security import check_password_hash

from db import *
from UserLogin import UserLogin

# configurate
DATABASE = '/tmp/app.db'
DEBUG = True
SECRET_KEY = 'vovan'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'app.db')))

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
    if hasattr(g, 'link_db'):
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


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # db= get_db()
    doc = database.get_doctor(current_user.get_id())
    return render_template("profile.html", doctor=doc, receptions=database.get_doctor_receptions(doc['id'])[:5])


@app.route('/admissions_history')
@login_required
def admissions_history():
    doc = database.get_doctor(current_user.get_id())
    return render_template("admissions_history.html", receptions=database.get_doctor_receptions(doc['id']))


@app.route('/add_admission/<int:animal_id>', methods=['POST', 'GET'])
@login_required
def add_admission(animal_id):
    if request.method == 'POST':
        description = request.form['description']
        research = request.form['research']
        diagnosis = request.form['diagnosis']
        recommendation = request.form['recommendation']
        doctor_id = database.get_doctor(current_user.get_id())['id']
        database.insert_reception(animal_id, doctor_id, '2022-12-11', '19:00:00', description,
                                  research, diagnosis, recommendation)
        return redirect(url_for('admissions', animal_id=animal_id))
    return render_template('add_admission.html', animal_id=animal_id)


@app.route('/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # вот тут данные из формы
        id = database.get_doctor(current_user.get_id())['id']
        surname = request.form['surname']
        name = request.form['name']
        patronymic = request.form['patronymic']
        qualification = request.form['qualification']
        database.update_doctor_info(id, surname, name, patronymic, qualification)
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', doctor=database.get_doctor(current_user.get_id()))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        req = request.form['login']
        if req == '':
            req = 0
        user = database.get_doctor(req)
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


@app.route('/', methods=['POST', 'GET'])
@login_required
def alm_library():
    if request.method == 'POST':
        database.delete_all_clients()
        return redirect(url_for('alm_library'))
    return render_template('alm_library.html', persons=database.get_all_clients())


@app.route('/animals/<int:id>', methods=['POST', 'GET'])
@login_required
def alm_animals(id):
    if request.method == 'POST':
        # вот тут по id удаляй клиента, т.к. нажата кнопка. Из реквеста брать ничего не надо.
        database.delete_client(id)
        return redirect(url_for('alm_library'))
    return render_template('alm_animals.html', animals=database.get_animals(id),
                           person=database.get_client(id), id=id)


@app.route('/admissions/<int:animal_id>')
@login_required
def admissions(animal_id):
    return render_template('admissions.html', receptions=database.get_animal_receptions(animal_id), animal_id=animal_id)


@app.route('/admission/<int:reception_id>')
@login_required
def admission(reception_id):

    return render_template("admission.html", info=database.get_reception(reception_id))


@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    if request.method == 'POST':
        # вот тут надо вызвать селекты и в persons закинуть результат поиска
        searcher = request.form['search']
        return redirect(url_for('search', searcher=searcher, status='progress'))
    searcher = request.args['searcher']
    status = request.args['status']
    return render_template("search.html", persons=database.get_by_last_name(searcher), status=status, req=searcher)


@app.route('/add_client', methods=['POST', 'GET'])
@login_required
def add_client():
    if request.method == 'POST':
        surname = request.form['surname']
        name = request.form['name']
        patronymic = request.form['patronymic']
        phone = request.form['phone']
        database.insert_client(phone, surname, name, patronymic)
        return redirect(url_for('alm_library'))
    return render_template("add_client.html")


@app.route('/add_animal/<int:client_id>', methods=['POST', 'GET'])
@login_required
def add_animal(client_id):
    if request.method == 'POST':
        nickname = request.form['nickname']
        gender = request.form['gender']
        age = int(request.form['age'])
        type = request.form['type']
        breed = request.form['breed']
        color = request.form['color']
        database.insert_animal(client_id, nickname, gender, age, type, breed, color)
        return redirect(url_for('alm_animals', id=client_id))

    return render_template("add_animal.html", client_id=client_id)


# @app.route('/search/result')
# @login_required
# def search_result():
#     searcher = request.args['searcher']
#     return render_template("search_result.html", persons = database.get_by_last_name(searcher))

if __name__ == "__main__":
    app.run(debug=True)
