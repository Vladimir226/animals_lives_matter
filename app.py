from flask import Flask, render_template, request, g, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
import sqlite3

from werkzeug.security import check_password_hash

from db import *
from UserLogin import UserLogin

# configurate
UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
DATABASE = '/tmp/app.db'
DEBUG = True
SECRET_KEY = 'vovan'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'app.db')))

database = ALM("usr", "123456", "localhost", "5432")

flag = True
if flag:
    database.insert_client(9990000001, 'Петров', 'Петр', 'Петрович')
    database.insert_client(9990000002, 'Иванов', 'Петр', 'Петрович')
    database.insert_client(9990000003, 'Иванов', 'Петр', 'Петрович')
    database.insert_client(9990000004, 'Ивановский', 'Петр', 'Петрович')

    database.insert_animal(1, 'Тузик', 'male', 5, 'Псовые', 'Дворняга', 'Черный')
    database.insert_animal(1, 'Буся', 'female', 1, 'Псовые', 'Акита-ину', 'Бело-рыжий')
    database.insert_animal(1, 'Муся', 'female', 2, 'Кошачьи', 'Шотландская вислоухая', 'Бело-серый')
    database.insert_animal(2, 'Рекс', 'male', 2, 'Псовые', 'Бульдог', 'Черный')
    database.insert_animal(2, 'Кета', 'male', 1, 'Попугаевые', 'Ара', 'Разноцветный')
    database.insert_animal(3, 'Ральф', 'female', 4, 'Псовые', 'Алабай', 'Белый')
    database.insert_animal(3, 'Барсик', 'male', 2, 'Кошачьи', 'Абиссинская', 'Рыжий')
    database.insert_animal(4, 'Пушок', 'male', 1, 'Хомяковые', 'Сирийский', 'Рыжий')
    database.insert_animal(4, 'Омега', 'female', 1, 'Свинья', 'Карликовая домашняя', 'Белая')

    database.insert_doctor(8000000001, 'Терапевт', 'xxx', 'Лебедев', 'Аркадий', 'Иванович')
    database.insert_doctor(8000000002, 'Терапевт', 'xxx', 'Попов', 'Василий', 'Михайлович')
    database.insert_doctor(8000000003, 'Хирург', 'xxx', 'Орлов', 'Александр', 'Вячеславович')

    database.insert_reception(1, 4, '2022-12-01', '11:35:00', 'Рана на лапе', '', 'Ранение',
                              'Смена повязки каждый день.')
    database.insert_reception(1, 2, '2022-12-05', '10:30:00', 'Кашель', 'Анализ крови', 'Простуда',
                     'Муколетики, тепло одеть собаку.')
    database.insert_reception(1, 2, '2022-12-10', '10:30:00', 'Выписка с ОРЗ', 'Анализ крови', 'Здоров',
                              'На прогулки одевать на животного одежду, гулять не более часа.')
    database.insert_reception(2, 3, '2022-12-08', '9:30:00', 'Кашель', 'Анализ крови', 'Простуда',
                              'Муколетики, тепло одеть собаку.')
    database.insert_reception(3, 3, '2022-12-06', '10:30:00', 'Кошка чешется.', 'Анализ шерсти', 'Блохи',
                              'Помыть кошку с специальным шампунем.')



login_manager = LoginManager(app)
login_manager.login_view = 'login'


def phone_parser(phone):
    phone = phone[2:].replace('(', "")
    phone = phone.replace(')', "")
    phone = phone.replace('-', "")
    return phone


@login_manager.user_loader
def load_user(user_phone):
    print("loader user")
    return UserLogin().fromDB(user_phone)


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
    if current_user.is_authenticated:
        if database.get_doctor(current_user.get_id()) == {}:
            logout_user()
            return redirect(url_for('profile'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
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
        date = request.form['date']
        time = request.form.get('clock')
        description = request.form['description']
        research = request.form['research']
        diagnosis = request.form['diagnosis']
        recommendation = request.form['recommendation']
        doctor_id = database.get_doctor(current_user.get_id())['id']
        database.insert_reception(animal_id, doctor_id, date, time, description,
                                  research, diagnosis, recommendation)
        return redirect(url_for('admissions', animal_id=animal_id))
    return render_template('add_admission.html', animal_id=animal_id)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    if request.method == 'POST':
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
        req = phone_parser(request.form['login'])
        if req == '':
            req = 0
        user = database.get_doctor(req)
        if user and check_password_hash(user['password'], request.form['password']):
            userlogin = UserLogin().create(user['phone_number'])
            login_user(userlogin)
            return redirect(url_for('profile'))
        else:
            flash('Неверная пара логин/пароль', category='error')
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
        phone = phone_parser(request.form['phone'])
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


@app.route('/super_doctor', methods=['POST', 'GET'])
@login_required
def super_doctor():
    if current_user.get_id() != '0':
        return redirect(url_for('alm_library'))
    if request.method == 'POST':
        database.delete_database()
        logout_user()
        return redirect(url_for('profile'))
    return render_template('super_profile.html', doctors=database.get_all_doctors())


@app.route('/add_doctor', methods=['POST', 'GET'])
@login_required
def add_doctor():
    if current_user.get_id() != '0':
        return redirect(url_for('alm_library'))
    if request.method == 'POST':
        surname = request.form['surname']
        name = request.form['name']
        patronymic = request.form['patronymic']
        phone = phone_parser(request.form['phone'])
        password = request.form['password']
        qualification = request.form['qualification']
        database.insert_doctor(phone, qualification, password, surname, name, patronymic)
        return redirect(url_for('super_doctor'))
    return render_template('add_doctor.html')


@app.errorhandler(404)
def not_found_error(error):
    return redirect('https://youtu.be/wxQV4rP-mJY?t=215')


if __name__ == "__main__":
    app.run(debug=False)
