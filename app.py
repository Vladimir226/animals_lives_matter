from flask import Flask, render_template, request, g 
import os
import sqlite3


#configurate
DATABASE = '/tmp/app.db'
DEBUG = True
SECRET_KEY = 'vovan'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'app.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g,'link_db'):
        g.link_db = connect_db()
    return g.link_db

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
    db= get_db()
    return render_template("profile.html",doctor = doctors[0])

@app.route('/admissions_history')
def admissions_history():
    return render_template("admissions_history.html")

@app.route('/add_admission')
def add_admission():
    return render_template('add_admission.html')

@app.route('/admission')
def admission():
    return render_template("admission.html")

@app.route('/edit_profile')
def edit_profile():
    return render_template('edit_profile.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def alm_library():
    return render_template('alm_library.html')

@app.route('/animals')
def alm_animals():
    return render_template('alm_animals.html')

@app.route('/animals/admisson')
def alm_admission():
    return render_template("admission.html")

if __name__ =="__main__":
    app.run(debug=True)